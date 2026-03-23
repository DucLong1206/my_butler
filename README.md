# My Butler Voice YouTube

Demo nhỏ giúp bạn mở video YouTube bằng lệnh nhập tay hoặc giọng nói.

## Cách dùng

1. API key YouTube đã được cấu hình sẵn trong `app.js`.
2. **Không mở trực tiếp bằng `file://` nếu bạn muốn điều khiển player**, vì YouTube embed có thể báo `Error 153` khi thiếu `HTTP Referer` / origin hợp lệ.
3. Chạy local server trong thư mục này bằng lệnh `python3 -m http.server 8000`.
4. Mở `http://localhost:8000` trong trình duyệt.
5. Nói hoặc nhập lệnh tìm kiếm như `mở video sơn tùng em của ngày hôm qua`.
6. Sau khi player mở ra, bạn có thể bấm nút hoặc nói các lệnh điều khiển như `tạm dừng`, `phát`, `phóng to`, `thu nhỏ`, `tốc độ 2x`, `tốc độ 1x`.

## Điểm chính

- Tìm video bằng YouTube Data API để cho kết quả chính xác hơn.
- Mở video trong `player.html` cùng nguồn gốc để trang chính có thể điều khiển video đang mở ngay lập tức.
- Nếu app bị mở bằng `file://`, trang chính sẽ không cố nhúng player nữa mà sẽ mở link YouTube trực tiếp để tránh lỗi `153`, đồng thời hướng dẫn bạn chuyển sang `http://localhost`.
- `player.html` truyền `origin` rõ ràng vào YouTube embed và lắng nghe lỗi player để báo nguyên nhân dễ hiểu hơn.
- Đọc trạng thái và kết quả bằng `speechSynthesis`, để bạn không cần nhìn màn hình liên tục.
- Nếu trình duyệt hỗ trợ `SpeechRecognition` / `webkitSpeechRecognition`, app có thể nghe lệnh bằng tiếng Việt.
- Có sẵn nút điều khiển nhanh cho phát, tạm dừng, phóng to, thu nhỏ, tốc độ 1x và 2x.

## Lưu ý

- Một số trình duyệt cần bạn thao tác trực tiếp (click) trước khi cho phép phát giọng nói, mở popup hoặc bật toàn màn hình.
- Nếu trình duyệt không hỗ trợ nhận diện giọng nói, bạn vẫn có thể nhập lệnh bằng bàn phím và bấm các nút điều khiển.
