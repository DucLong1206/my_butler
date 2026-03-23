# My Butler Voice YouTube

Demo nhỏ giúp bạn mở video YouTube bằng lệnh nhập tay hoặc giọng nói.

## Cách dùng

1. API key YouTube đã được cấu hình sẵn trong `app.js`.
2. Mở `index.html` trong trình duyệt.
3. Nhập lệnh như `mở video sơn tùng em của ngày hôm qua` hoặc bấm `🎤 Nói lệnh`.

## Điểm chính

- Tìm video bằng YouTube Data API để cho kết quả chính xác hơn.
- Tự động bỏ bớt các từ đầu câu như `mở`, `bật`, `tìm`, `play` trước khi gửi lên YouTube.
- Đọc trạng thái và kết quả bằng `speechSynthesis`, để bạn không cần nhìn màn hình liên tục.
- Nếu trình duyệt hỗ trợ `SpeechRecognition` / `webkitSpeechRecognition`, app có thể nghe lệnh bằng tiếng Việt.

## Lưu ý

- Một số trình duyệt cần bạn thao tác trực tiếp (click) trước khi cho phép phát giọng nói hoặc mở tab mới.
- Nếu trình duyệt không hỗ trợ nhận diện giọng nói, bạn vẫn có thể nhập lệnh bằng bàn phím.
