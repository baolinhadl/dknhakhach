# dknhakhach

Ứng dụng web nhỏ hỗ trợ quy trình đăng ký trước, duyệt và quản lý check-in/out khách đến thăm quân nhân tại nhà khách. Giao diện được xây dựng bằng Flask + Bootstrap, sử dụng SQLite mặc định (có thể trỏ tới MySQL/MariaDB qua biến `DATABASE_URL`).

## Tính năng chính
- Quản lý hồ sơ quân nhân để gắn với lượt thăm.
- Tiếp nhận đăng ký thăm (từ ngày/đến ngày, thông tin liên hệ) và lưu trạng thái chờ duyệt.
- Duyệt hoặc từ chối đăng ký, lưu thông tin người duyệt và thời gian duyệt.
- Check-in khách đã duyệt vào nhà khách, check-out khi rời đi, xem lịch sử gần nhất.
- Nút tạo dữ liệu mẫu phục vụ thử nhanh giao diện.

## Chuẩn bị môi trường
1. Cài đặt Python 3.10+.
2. Cài đặt dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Chạy ứng dụng
```bash
export FLASK_APP=app.py
flask run --host=0.0.0.0 --port=5000
```

- Lần đầu chạy sẽ tự tạo file SQLite `nhakhach.db` theo mô hình dữ liệu.
- Mở trình duyệt tại `http://localhost:5000`.
- Có thể tạo dữ liệu mẫu bằng nút "Tạo dữ liệu mẫu" trên trang chính.

## Cấu hình
- `DATABASE_URL`: kết nối cơ sở dữ liệu (mặc định `sqlite:///nhakhach.db`). Có thể trỏ đến MySQL/MariaDB nếu đã khởi tạo schema tương ứng.
- `SECRET_KEY`: khóa session Flask, đặt giá trị riêng khi chạy thật.

## Phù hợp với schema cung cấp
Các bảng và nghiệp vụ bám sát script SQL:
- `quannhan`, `dangky_thamthan`, `nhakhach_tham`, `tutuong` được ánh xạ thành model SQLAlchemy.
- Các thao tác duyệt, check-in/out và các danh sách hiển thị tương đương các view trong script (danh sách chờ duyệt, đang ở, lịch sử ra/vào, biểu mẫu).
