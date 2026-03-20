from __future__ import annotations

import threading
from queue import Queue
from typing import Optional


class VietnameseTTS:
    def __init__(self, rate: int = 175, volume: float = 1.0) -> None:
        self._queue: Queue[str] = Queue()
        self._engine = None
        self._rate = rate
        self._volume = volume
        self._lock = threading.Lock()
        self._init_engine()
        self._worker = threading.Thread(target=self._run, daemon=True)
        self._worker.start()

    def _init_engine(self) -> None:
        try:
            import pyttsx3

            self._engine = pyttsx3.init()
            self._engine.setProperty("rate", self._rate)
            self._engine.setProperty("volume", self._volume)

            selected_voice: Optional[str] = None
            for voice in self._engine.getProperty("voices"):
                name = f"{voice.name} {voice.id}".lower()
                if any(keyword in name for keyword in ("vietnam", "vi", "zira", "hanh")):
                    selected_voice = voice.id
                    break

            if selected_voice:
                self._engine.setProperty("voice", selected_voice)
                print(f"[TTS] Đã chọn voice: {selected_voice}")
            else:
                print("[TTS] Không tìm thấy voice tiếng Việt rõ ràng, dùng voice mặc định của hệ thống.")
        except Exception as exc:  # pylint: disable=broad-except
            print(f"[TTS] Không khởi tạo được pyttsx3: {exc}")
            self._engine = None

    def speak(self, text: str) -> None:
        cleaned = text.strip()
        if cleaned:
            print(f"[ASSISTANT] {cleaned}")
            self._queue.put(cleaned)

    def _run(self) -> None:
        while True:
            text = self._queue.get()
            if self._engine is None:
                continue
            with self._lock:
                try:
                    self._engine.say(text)
                    self._engine.runAndWait()
                except Exception as exc:  # pylint: disable=broad-except
                    print(f"[TTS] Lỗi phát âm thanh: {exc}")
