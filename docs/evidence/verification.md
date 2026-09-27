# Kết quả kiểm chứng Tutorial07

Ngày kiểm chứng: 27/09/2026 (Asia/Ho_Chi_Minh).

Repo tham chiếu: [thaycacac/ddm501/tutorial07](https://github.com/thaycacac/ddm501/tree/main/tutorial07), commit `b13ae9ce1e24a8c34916a2758c52f31c4618d0cf`.

## Các luồng đã chạy thực tế

| Kiểm tra | Kết quả quan sát |
|---|---|
| Dữ liệu bình thường | 178 samples được nạp; phân tích 100 samples gần nhất; drift 0/13 |
| Dữ liệu dịch 4 độ lệch chuẩn | Drift 13/13, score 1.0; report HTML được tạo |
| `drift_monitoring` / `evidence-shifted-data` | Thành công; nhánh alert và trigger retrain chạy, nhánh no_drift skipped đúng thiết kế |
| Retrain do drift | Run `manual__2026-09-27T10:17:46.353457+00:00` thành công; model v6 Production, API phục vụ v6 |
| Quality gate | `evidence-quality-gate-confirmed`: accuracy 1.0 < 1.01; v5 không được promote, các task downstream bị chặn |
| Telegram task failure | Bot DDM501-Tutorial07 nhận tên DAG, task, run ID và lý do quality gate thất bại |
| Prometheus / Alertmanager | APIDown firing/resolved, DataDriftDetected firing/resolved, AirflowDagFailed firing/resolved được gửi tới bot |
| Khôi phục dữ liệu | `seed_demo.py --analyze`: drift false, score 0.0, 0/13; prediction với model v6 thành công |
| Health check cuối | `evidence-final-healthy`: check_api, check_mlflow, check_evidently và report đều success |
| Drift check cuối | `evidence-final-no-drift`: nhánh no_drift success, alert/retrain skipped đúng thiết kế |
| DAG imports | `airflow dags list-import-errors`: No data found |
| Airflow dependencies | Rebuild image từ requirements hiện tại; `python -m pip check`: No broken requirements found |
| Prometheus targets | airflow, alertmanager, evidently, model-api, prometheus đều up |
| Docker Compose | 12 service thường trực đang chạy; tất cả service có healthcheck đều healthy |

Các ảnh PNG trong thư mục này chụp trực tiếp cửa sổ Telegram Desktop của bot **DDM501-Tutorial07** (`@mrduovn_bot`). Không chứa token/chat ID và không dùng ảnh từ repo mẫu.

## Phạm vi và giới hạn

GitHub Actions [run 36312100585](https://github.com/TrinhDucDuong/ddm501-Tutorial07-ml-monitoring-full-version/actions/runs/36312100585) đã **completed / success**, kiểm thử commit `9af85da13769fa5a71dbe1e334b5a507d709c5c0`. Tất cả bước kiểm tra và cleanup đều thành công; bước in log khi lỗi được skipped đúng thiết kế. Bản cập nhật evidence sau run này chỉ thay tài liệu.

- Đây là triển khai Docker Compose local. Model deployment là promote MLflow Production rồi reload API bởi Airflow; chưa cấu hình máy chủ cloud hay GitHub runner để triển khai từ xa.
- CI kiểm thử Compose, Python, Prometheus rules, train/register/predict, normal/drift và import 3 DAG. Các luồng Telegram và thực thi DAG ở bảng trên được kiểm thử local, không gửi Telegram trong CI.
- MinIO Dockerfile được build từ source release `RELEASE.2025-09-07T16-13-09Z` trong CI. Local dùng image MinIO cùng release đã có trong cache để tránh build nặng khi nhiều stack khác đang chạy.
- Có lịch sử DAG thất bại do kiểm thử cố ý và Docker Desktop bị gián đoạn trong quá trình chuẩn bị. Các lần chạy cuối nêu trên xác nhận hệ thống đã phục hồi; không xóa lịch sử kiểm thử.
- Accuracy 1.0 là kết quả trên tập kiểm thử nhỏ của dataset wine trong bài thực hành, không phải cam kết chất lượng dữ liệu thực tế. Retrain hiện dùng dataset wine của tutorial, chưa có nguồn nhãn production.
