# dknhakhach

Ứng dụng Flask đơn giản để quản lý đăng ký thăm nhà khách cho quân nhân.

## Cách chạy
1. Tạo virtualenv và cài đặt phụ thuộc:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Khởi tạo cơ sở dữ liệu SQLite:
   ```bash
   flask --app app.py init-db
   ```
3. Chạy ứng dụng:
   ```bash
   flask --app app.py --debug run
   ```

Ứng dụng sẽ chạy tại http://localhost:5000.

## Chức năng chính
- Thêm quân nhân (thông tin cá nhân, đơn vị, cấp bậc...).
- Đăng ký trước lịch thăm (từ ngày/đến ngày, người thăm, quan hệ, số điện thoại, ghi chú).
- Duyệt/Từ chối đăng ký.
- Check-in khách đã được duyệt và đánh dấu rời khỏi nhà khách.
- Bảng điều khiển tổng quan thể hiện hồ sơ chờ duyệt, đã duyệt, khách đang ở và lịch sử gần đây.

## Ghi chú
- Ứng dụng sử dụng SQLite cho mục đích demo. Có thể thay đổi `SQLALCHEMY_DATABASE_URI` trong `app.py` để kết nối MySQL/MariaDB phù hợp với schema cung cấp.
- Flash message sử dụng `SECRET_KEY` tĩnh cho môi trường phát triển; thay đổi khi triển khai thật.
