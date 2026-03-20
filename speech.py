from __future__ import annotations

import json
import os
import queue
import time
from dataclasses import dataclass
from typing import Optional


@dataclass
class RecognitionResult:
    text: str
    engine: str


class SpeechListener:
    """Ưu tiên nhận diện offline bằng Vosk, fallback online bằng SpeechRecognition."""

    def __init__(self) -> None:
        self.vosk_model_path = os.getenv("VOSK_MODEL_PATH", "models/vosk-model-small-vn-0.4")
        self.sample_rate = int(os.getenv("VOSK_SAMPLE_RATE", "16000"))
        self.energy_threshold = int(os.getenv("SR_ENERGY_THRESHOLD", "300"))
        self._audio_queue: queue.Queue[bytes] = queue.Queue()
        self._vosk_ready = False
        self._recognizer = None
        self._stream = None
        self._speech_recognition = None
        self._sr_recognizer = None
        self._init_engines()

    def _init_engines(self) -> None:
        try:
            from vosk import KaldiRecognizer, Model  # type: ignore
            import sounddevice as sd  # type: ignore

            if os.path.isdir(self.vosk_model_path):
                print(f"[SPEECH] Đang nạp Vosk model: {self.vosk_model_path}")
                model = Model(self.vosk_model_path)
                self._recognizer = KaldiRecognizer(model, self.sample_rate)

                def _callback(indata, frames, time_info, status) -> None:  # type: ignore
                    if status:
                        print(f"[SPEECH][VOSK] Stream status: {status}")
                    self._audio_queue.put(bytes(indata))

                self._stream = sd.RawInputStream(
                    samplerate=self.sample_rate,
                    blocksize=8000,
                    dtype="int16",
                    channels=1,
                    callback=_callback,
                )
                self._stream.start()
                self._vosk_ready = True
                print("[SPEECH] Vosk offline đã sẵn sàng.")
            else:
                print(
                    "[SPEECH] Không tìm thấy model Vosk. "
                    f"Hãy tải model tiếng Việt và đặt tại: {self.vosk_model_path}"
                )
        except Exception as exc:  # pylint: disable=broad-except
            print(f"[SPEECH] Không khởi tạo được Vosk: {exc}")

        if not self._vosk_ready:
            self._init_speech_recognition()

    def _init_speech_recognition(self) -> None:
        try:
            import speech_recognition as sr  # type: ignore

            self._speech_recognition = sr
            self._sr_recognizer = sr.Recognizer()
            self._sr_recognizer.energy_threshold = self.energy_threshold
            self._sr_recognizer.pause_threshold = 0.8
            self._sr_recognizer.dynamic_energy_threshold = True
            print("[SPEECH] Fallback SpeechRecognition đã sẵn sàng.")
        except Exception as exc:  # pylint: disable=broad-except
            print(f"[SPEECH] Không thể khởi tạo SpeechRecognition: {exc}")

    def listen_for_text(self, timeout: int = 8) -> str:
        result = self._listen_once(timeout=timeout)
        return result.text if result else ""

    def _listen_once(self, timeout: int = 8) -> Optional[RecognitionResult]:
        if self._vosk_ready:
            result = self._listen_with_vosk(timeout=timeout)
            if result and result.text:
                return result

        if self._sr_recognizer is not None:
            return self._listen_with_google(timeout=timeout)

        return None

    def _listen_with_vosk(self, timeout: int = 8) -> Optional[RecognitionResult]:
        print("[SPEECH] Đang nghe bằng Vosk...")
        started = time.time()
        partial_text = ""

        while time.time() - started < timeout:
            try:
                data = self._audio_queue.get(timeout=0.25)
            except queue.Empty:
                continue

            if self._recognizer.AcceptWaveform(data):  # type: ignore[union-attr]
                payload = json.loads(self._recognizer.Result())  # type: ignore[union-attr]
                text = payload.get("text", "").strip()
                if text:
                    return RecognitionResult(text=text, engine="vosk")
            else:
                payload = json.loads(self._recognizer.PartialResult())  # type: ignore[union-attr]
                partial_text = payload.get("partial", "").strip()

        if partial_text:
            return RecognitionResult(text=partial_text, engine="vosk-partial")
        return None

    def _listen_with_google(self, timeout: int = 8) -> Optional[RecognitionResult]:
        sr = self._speech_recognition
        print("[SPEECH] Đang nghe bằng Google SpeechRecognition...")
        if sr is None or self._sr_recognizer is None:
            return None

        try:
            with sr.Microphone() as source:
                self._sr_recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self._sr_recognizer.listen(source, timeout=timeout, phrase_time_limit=timeout)
            text = self._sr_recognizer.recognize_google(audio, language="vi-VN")
            return RecognitionResult(text=text.lower().strip(), engine="google")
        except sr.WaitTimeoutError:
            print("[SPEECH] Không nghe thấy câu lệnh nào.")
        except sr.UnknownValueError:
            print("[SPEECH] Không nhận dạng được nội dung giọng nói.")
        except Exception as exc:  # pylint: disable=broad-except
            print(f"[SPEECH] Lỗi SpeechRecognition: {exc}")
        return None
