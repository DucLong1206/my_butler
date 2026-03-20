# My Butler - Trợ lý giọng nói Windows

Một trợ lý ảo Python chạy nền kiểu "Jarvis mini" dành cho Windows. Ứng dụng luôn lắng nghe, chỉ phản hồi khi nghe thấy wake word **"Long ơi"** hoặc **"Hey Long"**, sau đó xử lý các lệnh cơ bản bằng tiếng Việt.

## Tính năng chính

- Luôn chạy nền, vòng lặp ổn định và nhẹ CPU.
- Ưu tiên nhận diện giọng nói **offline bằng Vosk**.
- Tự động fallback sang **SpeechRecognition + Google** nếu chưa có Vosk model.
- Phản hồi giọng nói bằng **pyttsx3** theo phong cách thân thiện, gọi người dùng là **sếp**.
- Xử lý các lệnh:
  - Bật nhạc trên YouTube.
  - Xem thời tiết Hà Nội qua OpenWeatherMap.
  - Xem giờ hệ thống.
  - Mở Messenger Web / WhatsApp Web và kiểm tra unread ở mức cơ bản.
- In log chi tiết ra console để debug.

## Cấu trúc file

- `main.py`: Vòng lặp chính, wake word, điều phối.
- `speech.py`: Nhận diện giọng nói, ưu tiên Vosk.
- `tts.py`: Text-to-speech bằng pyttsx3.
- `commands.py`: Xử lý các câu lệnh if/else.
- `requirements.txt`: Danh sách thư viện cần cài.

## Cài thư viện

### 1) Tạo môi trường ảo (khuyến nghị)

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 2) Cài dependencies

```bash
pip install -r requirements.txt
```

Nếu `speech_recognition` cần thêm driver microphone trên Windows, có thể cài thêm:

```bash
pip install pyaudio
```

> Lưu ý: `pyaudio` đôi khi khó cài trên Windows. Nếu vậy bạn vẫn có thể dùng đường nhận diện **Vosk + sounddevice**.

## Chuẩn bị Vosk tiếng Việt (khuyên dùng)

Tải một model tiếng Việt của Vosk, ví dụ model nhỏ, rồi giải nén vào thư mục:

```text
models/vosk-model-small-vn-0.4
```

Hoặc set biến môi trường:

```bash
set VOSK_MODEL_PATH=D:\path\to\vosk-model-small-vn-0.4
```

## Cấu hình biến môi trường

### 1) OpenWeatherMap API key

Đăng ký API key tại OpenWeatherMap rồi set:

```bash
set OPENWEATHER_API_KEY=your_api_key_here
```

### 2) Tuỳ chọn Chrome / Selenium

Nếu muốn mở đúng Chrome hoặc tự click kết quả YouTube đầu tiên bằng Selenium:

```bash
set CHROME_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe
set CHROMEDRIVER_PATH=C:\tools\chromedriver.exe
```

Nếu muốn dùng profile Chrome đang đăng nhập sẵn Messenger / WhatsApp:

```bash
set CHROME_PROFILE=C:\Users\YourUser\AppData\Local\Google\Chrome\User Data
```

### 3) Chọn nền tảng kiểm tra tin nhắn

Mặc định dùng Messenger. Nếu muốn WhatsApp Web:

```bash
set MESSAGE_TARGET=whatsapp
```

## Cách chạy chương trình

```bash
python main.py
```

Sau khi chạy, trợ lý sẽ luôn lắng nghe trong nền. Chỉ khi nghe thấy:

- `Long ơi`
- `Hey Long`

thì mới bắt đầu xử lý tiếp nội dung phía sau.

## Ví dụ lệnh hỗ trợ

- `Long ơi bật nhạc Sơn Tùng`
- `Hey Long hôm nay bao nhiêu độ`
- `Long ơi mấy giờ rồi`
- `Long ơi có tin nhắn không`

## Cách hoạt động

### 1) Bật nhạc

- Trợ lý phân tích phần từ khoá sau cụm `bật nhạc`.
- Mở YouTube search bằng trình duyệt.
- Nếu có cấu hình `CHROMEDRIVER_PATH`, trợ lý sẽ cố click vào video đầu tiên.
- Nếu không có Selenium, trợ lý vẫn mở sẵn trang kết quả để bạn chọn nhanh.

### 2) Xem thời tiết

- Gọi API OpenWeatherMap.
- Đọc nhiệt độ hiện tại ở Hà Nội.
- Nếu thiếu API key, trợ lý sẽ báo rõ để bạn bổ sung.

### 3) Kiểm tra tin nhắn

- Mở Messenger Web hoặc WhatsApp Web.
- Nếu có Selenium + phiên đăng nhập sẵn, trợ lý sẽ thử đọc title tab để suy ra số chưa đọc.
- Đây là mức kiểm tra **cơ bản**, phù hợp yêu cầu demo / mini assistant.

## Mẹo để chạy mượt và nhẹ CPU

- Dùng model **Vosk small** để tiết kiệm tài nguyên.
- Chỉ xử lý lệnh khi có wake word nên CPU nhẹ hơn nhiều.
- Vòng lặp chính có sleep ngắn để tránh busy-wait.
- TTS chạy bằng thread riêng, tránh khóa vòng lặp nghe.

## Lưu ý thực tế trên Windows

- pyttsx3 sẽ dùng voice của Windows; nên cài voice tiếng Việt nếu muốn đọc tự nhiên hơn.
- Selenium chỉ tự click / tự đọc title tốt khi Chrome và chromedriver tương thích version.
- Messenger / WhatsApp Web thường yêu cầu đăng nhập trước trên profile trình duyệt của bạn.

## Hướng mở rộng tiếp theo

- Thêm lệnh mở ứng dụng desktop (Notepad, Word, VS Code).
- Thêm lịch nhắc việc / báo thức.
- Dùng intent matching thông minh hơn thay vì if/else.
- Thêm hotword detector chuyên dụng để wake word ổn định hơn.
