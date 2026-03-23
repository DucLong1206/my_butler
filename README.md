# My Butler Voice YouTube

Demo nhỏ giúp bạn mở video YouTube bằng lệnh nhập tay hoặc giọng nói.

## Cách dùng

1. API key YouTube đã được cấu hình sẵn trong `app.js`.
2. Mở `index.html` trong trình duyệt.
3. Nói hoặc nhập lệnh tìm kiếm như `mở video sơn tùng em của ngày hôm qua`.
4. Sau khi player mở ra, bạn có thể bấm nút hoặc nói các lệnh điều khiển như `tạm dừng`, `phát`, `phóng to`, `thu nhỏ`, `tốc độ 2x`, `tốc độ 1x`.

## Điểm chính

- Tìm video bằng YouTube Data API để cho kết quả chính xác hơn.
- Mở video trong `player.html` cùng nguồn gốc để trang chính có thể điều khiển video đang mở ngay lập tức.
- Đọc trạng thái và kết quả bằng `speechSynthesis`, để bạn không cần nhìn màn hình liên tục.
- Nếu trình duyệt hỗ trợ `SpeechRecognition` / `webkitSpeechRecognition`, app có thể nghe lệnh bằng tiếng Việt.
- Có sẵn nút điều khiển nhanh cho phát, tạm dừng, phóng to, thu nhỏ, tốc độ 1x và 2x.

## Lưu ý

- Một số trình duyệt cần bạn thao tác trực tiếp (click) trước khi cho phép phát giọng nói, mở popup hoặc bật toàn màn hình.
- Nếu trình duyệt không hỗ trợ nhận diện giọng nói, bạn vẫn có thể nhập lệnh bằng bàn phím và bấm các nút điều khiển.
