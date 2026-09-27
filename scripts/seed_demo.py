"""Prepare deterministic wine data and verify real prediction/drift endpoints."""
import argparse
import json
import os
import urllib.request
import numpy as np

from sklearn.datasets import load_wine


def request(url, data=None, method=None):
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, method=method, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as response:
        return json.load(response)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--drift", action="store_true", help="Shift every feature by four standard deviations")
    parser.add_argument("--analyze", action="store_true", help="Run and assert the expected drift result")
    args = parser.parse_args()
    api = os.getenv("API_URL", "http://api:8000")
    evidently = os.getenv("EVIDENTLY_URL", "http://evidently:8001")
    wine = load_wine()
    # load_wine is ordered by class; shuffle so the final analysis window is representative.
    wine.data = wine.data[np.random.default_rng(42).permutation(len(wine.data))]
    reference = [dict(zip(wine.feature_names, row.tolist())) for row in wine.data]
    current = wine.data + 4 * wine.data.std(axis=0) if args.drift else wine.data.copy()
    request(api + "/model/reload", {})
    health = request(api + "/health")
    assert health["model_loaded"], health
    prediction = request(api + "/predict", {"features": current[0].tolist()})
    assert prediction["prediction"] in (0, 1, 2), prediction
    request(evidently + "/reference", {"data": reference, "feature_names": wine.feature_names, "description": "Deterministic sklearn wine tutorial baseline"})
    request(evidently + "/production-data", method="DELETE")
    request(evidently + "/capture/batch", {"data": [dict(zip(wine.feature_names, row.tolist())) for row in current]})
    print(f"Model v{health['model_version']}: prediction OK; seeded {len(current)} samples (drift={args.drift})")
    if args.analyze:
        result = request(evidently + "/analyze", {"window_size": len(current), "threshold": 0.1})
        assert bool(result["drift_detected"]) == args.drift, result
        assert (result["drifted_count"] > 0) == args.drift, result
        assert len(result["drift_scores"]) == 13, result
        print(json.dumps({key: result[key] for key in ("drift_detected", "drift_score", "drifted_count", "total_features", "report_url")}, indent=2))


if __name__ == "__main__":
    main()
