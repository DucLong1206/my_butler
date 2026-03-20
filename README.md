# My Butler - Trợ lý giọng nói Windows

Một trợ lý ảo Python chạy nền kiểu "Jarvis mini" dành cho Windows. Ứng dụng luôn lắng nghe, chỉ phản hồi khi nghe thấy wake word **"Long ơi"**, **"long oi"**, **"Hey Long"** hoặc **"Long"** ở đầu câu, sau đó xử lý các lệnh cơ bản bằng tiếng Việt.

## Tính năng chính

- Luôn chạy nền, vòng lặp ổn định và nhẹ CPU.
- Ưu tiên nhận diện giọng nói **offline bằng Vosk**.
- Tự động fallback sang **SpeechRecognition + Google** nếu chưa có Vosk model.
- **Không phụ thuộc PyAudio** cho đường fallback online: microphone vẫn thu bằng `sounddevice` rồi mới đưa sang Google SpeechRecognition.
- In log debug rõ hơn để biết micro có đang thu âm hay không:
  - Mức âm lượng RMS hiện tại.
  - Partial text khi Vosk đang nghe.
  - Tổng số byte / thời lượng âm thanh đã thu ở đường fallback.
- Phản hồi giọng nói bằng **pyttsx3** theo phong cách thân thiện, gọi người dùng là **sếp**.
- Xử lý các lệnh:
  - Bật nhạc trên YouTube.
  - Xem thời tiết Hà Nội qua OpenWeatherMap.
  - Xem giờ hệ thống.
  - Mở Messenger Web / WhatsApp Web và kiểm tra unread ở mức cơ bản.

## Cấu trúc file

- `main.py`: Vòng lặp chính, wake word, điều phối.
- `speech.py`: Nhận diện giọng nói, ưu tiên Vosk, fallback online không cần PyAudio.
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

> Bản hiện tại **không yêu cầu PyAudio** để fallback online nữa. Nếu trước đó bạn thấy lỗi `Could not find PyAudio`, hãy pull bản code mới này rồi chạy lại.

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

### 4) Tuỳ chỉnh debug audio

Mặc định đang bật debug để bạn dễ kiểm tra micro có thu được âm thanh không:

```bash
set DEBUG_AUDIO=1
```

Nếu muốn bớt log:

```bash
set DEBUG_AUDIO=0
```

Có thể chỉnh ngưỡng phát hiện giọng nói nếu micro quá nhỏ hoặc quá nhạy:

```bash
set SR_ENERGY_THRESHOLD=300
set SR_SILENCE_TIMEOUT=1.2
set SR_MAX_PHRASE_SECONDS=6
```

## Cách chạy chương trình

```bash
python main.py
```

Khi chạy, bạn có thể quan sát log như sau:

- `[MIC] RMS=...` → micro đang thu được mức âm lượng bao nhiêu.
- `[SPEECH][PARTIAL] ...` → Vosk đang nghe được từng phần gì.
- `[HEARD] ...` → câu đã nhận diện xong.
- `[MIC][IDLE] backend=... rms=... partial='...'` → snapshot nhanh khi chưa có câu lệnh hoàn chỉnh.

## Ví dụ lệnh hỗ trợ

- `Long ơi bật nhạc Sơn Tùng`
- `long oi mở nhạc lofi`
- `Hey Long hôm nay bao nhiêu độ`
- `Long mấy giờ rồi`
- `Long có tin nhắn không`

## Cách xử lý lỗi wake word không ăn

Nếu bạn nói mà trợ lý không phản hồi:

1. Nhìn log `RMS`:
   - Nếu luôn gần `0` → Windows chưa lấy đúng microphone.
   - Nếu có tăng mạnh nhưng không ra text → speech engine chưa hiểu rõ giọng nói.
2. Thử nói chậm và rõ hơn:
   - `Long ơi`
   - `long oi`
   - `Hey Long`
   - `Long mở nhạc lofi`
3. Nếu đang fallback online, kiểm tra Internet.
4. Nếu muốn ổn định hơn, nên dùng Vosk model tiếng Việt offline.

## Mẹo để chạy mượt và nhẹ CPU

- Dùng model **Vosk small** để tiết kiệm tài nguyên.
- Chỉ xử lý lệnh khi có wake word nên CPU nhẹ hơn nhiều.
- Vòng lặp chính có sleep ngắn để tránh busy-wait.
- TTS chạy bằng thread riêng, tránh khóa vòng lặp nghe.

## Lưu ý thực tế trên Windows

- pyttsx3 sẽ dùng voice của Windows; nên cài voice tiếng Việt nếu muốn đọc tự nhiên hơn.
- Selenium chỉ tự click / tự đọc title tốt khi Chrome và chromedriver tương thích version.
- Messenger / WhatsApp Web thường yêu cầu đăng nhập trước trên profile trình duyệt của bạn.
- Nếu bạn muốn kiểm tra micro đang nhận âm trực tiếp, chỉ cần xem log `RMS` là đủ để debug nhanh.
