# Report Lab 16 - AWS CPU Fallback

## Thông tin sinh viên

- Họ và tên: Lê Minh Hoàng
- MSSV: 2A202600101

## Tóm tắt triển khai

Em triển khai phương án CPU fallback trên AWS thay cho phương án GPU vì tài khoản AWS mới không có quota GPU và không thể tạo instance `g4dn.xlarge`.

Theo `README_aws.md`, phương án CPU đề xuất sử dụng `r5.2xlarge`. Tuy nhiên, khi chạy `terraform apply`, AWS trả về lỗi cho biết loại instance này không đủ điều kiện cho Free Tier. Vì vậy, em đã điều chỉnh sang `t3.micro` để phù hợp với giới hạn của tài khoản.

Hạ tầng vẫn được triển khai đầy đủ bằng Terraform, bao gồm:

- VPC
- Public subnet
- Private subnet
- Bastion Host
- Private CPU node
- NAT Gateway
- Application Load Balancer

Trên CPU node, em cài đặt môi trường Python và thực hiện benchmark LightGBM với bộ dữ liệu `Credit Card Fraud Detection` tải từ Kaggle.

## Kết quả benchmark

| Chỉ số | Giá trị |
| --- | --- |
| Dataset | `creditcard.csv` |
| Số dòng dữ liệu | 284807 |
| Số đặc trưng | 30 |
| Load time | 2.465 s |
| Training time | 2.0061 s |
| Prediction time | 0.0135 s |
| Best iteration | 1 |
| AUC-ROC | 0.9516 |
| Accuracy | 0.998947 |
| F1-score | 0.727273 |
| Precision | 0.655738 |
| Recall | 0.816327 |
| Inference latency (1 row) | 1.7059 ms |
| Inference throughput (1000 rows) | 581807.35 rows/s |
| Total runtime | 4.8617 s |

## Ghi chú về chi phí

AWS Billing và Cost Explorer chưa hiển thị dữ liệu ngay, đồng thời hệ thống thông báo cần tối đa 24 giờ để chuẩn bị `cost and usage data`. Vì vậy, em đã chụp lại thông báo này để làm minh chứng.

Sau khi hoàn thành benchmark và thu thập kết quả, em đã chạy `terraform destroy` để xóa toàn bộ tài nguyên nhằm tránh phát sinh thêm chi phí.
