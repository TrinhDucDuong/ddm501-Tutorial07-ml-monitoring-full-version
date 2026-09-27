"""Trigger the demo DAGs without shell-specific JSON quoting."""
import argparse
import json
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("dag", choices=["service_health_check", "drift_monitoring", "model_retrain"])
parser.add_argument("--run-id")
parser.add_argument("--min-accuracy", type=float)
parser.add_argument("--reason", default="manual tutorial demo")
args = parser.parse_args()
config = {"reason": args.reason}
if args.min_accuracy is not None:
    config["min_accuracy"] = args.min_accuracy
command = ["docker", "compose", "exec", "-T", "airflow-scheduler", "airflow", "dags", "trigger", args.dag, "--conf", json.dumps(config)]
if args.run_id:
    command.extend(["--run-id", args.run_id])
subprocess.run(command, check=True)
