from __future__ import annotations

import audioop
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
    """Ưu tiên Vosk offline; fallback online qua SpeechRecognition nhưng vẫn thu âm bằng sounddevice."""

    def __init__(self) -> None:
        self.vosk_model_path = os.getenv("VOSK_MODEL_PATH", "models/vosk-model-small-vn-0.4")
        self.sample_rate = int(os.getenv("VOSK_SAMPLE_RATE", "16000"))
        self.energy_threshold = int(os.getenv("SR_ENERGY_THRESHOLD", "300"))
        self.silence_timeout = float(os.getenv("SR_SILENCE_TIMEOUT", "1.2"))
        self.max_phrase_seconds = int(os.getenv("SR_MAX_PHRASE_SECONDS", "6"))
        self.debug_audio = os.getenv("DEBUG_AUDIO", "1") == "1"
        self._audio_queue: queue.Queue[bytes] = queue.Queue()
        self._vosk_ready = False
        self._recognizer = None
        self._stream = None
        self._speech_recognition = None
        self._sr_recognizer = None
        self._last_rms = 0
        self._last_partial_text = ""
        self._last_debug_print = 0.0
        self._init_engines()

    def _init_engines(self) -> None:
        self._init_vosk_stream()
        self._init_speech_recognition()

    def _init_vosk_stream(self) -> None:
        try:
            from vosk import KaldiRecognizer, Model  # type: ignore
            import sounddevice as sd  # type: ignore

            if not os.path.isdir(self.vosk_model_path):
                print(
                    "[SPEECH] Không tìm thấy model Vosk. "
                    f"Sẽ fallback online, model mong đợi tại: {self.vosk_model_path}"
                )
                return

            print(f"[SPEECH] Đang nạp Vosk model: {self.vosk_model_path}")
            model = Model(self.vosk_model_path)
            self._recognizer = KaldiRecognizer(model, self.sample_rate)

            def _callback(indata, frames, time_info, status) -> None:  # type: ignore
                del frames, time_info
                if status:
                    print(f"[SPEECH][VOSK] Stream status: {status}")
                chunk = bytes(indata)
                self._last_rms = audioop.rms(chunk, 2)
                if self.debug_audio and self._last_rms > 0:
                    now = time.time()
                    if now - self._last_debug_print > 1.0:
                        print(f"[MIC] RMS={self._last_rms} | backend=vosk")
                        self._last_debug_print = now
                self._audio_queue.put(chunk)

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
        except Exception as exc:  # pylint: disable=broad-except
            print(f"[SPEECH] Không khởi tạo được Vosk stream: {exc}")

    def _init_speech_recognition(self) -> None:
        try:
            import speech_recognition as sr  # type: ignore

            self._speech_recognition = sr
            self._sr_recognizer = sr.Recognizer()
            self._sr_recognizer.energy_threshold = self.energy_threshold
            self._sr_recognizer.pause_threshold = 0.8
            self._sr_recognizer.dynamic_energy_threshold = True
            print("[SPEECH] SpeechRecognition đã sẵn sàng cho fallback online (không cần PyAudio).")
        except Exception as exc:  # pylint: disable=broad-except
            print(f"[SPEECH] Không thể khởi tạo SpeechRecognition: {exc}")

    def listen_for_text(self, timeout: int = 8) -> str:
        result = self._listen_once(timeout=timeout)
        return result.text if result else ""

    def print_debug_snapshot(self, prefix: str = "[MIC]") -> None:
        print(
            f"{prefix} backend={'vosk' if self._vosk_ready else 'google-fallback'} "
            f"rms={self._last_rms} partial='{self._last_partial_text}'"
        )

    def _listen_once(self, timeout: int = 8) -> Optional[RecognitionResult]:
        if self._vosk_ready:
            result = self._listen_with_vosk(timeout=timeout)
            if result and result.text:
                return result

        if self._sr_recognizer is not None:
            return self._listen_with_google_via_sounddevice(timeout=timeout)

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
                    self._last_partial_text = text
                    return RecognitionResult(text=text, engine="vosk")
            else:
                payload = json.loads(self._recognizer.PartialResult())  # type: ignore[union-attr]
                partial_text = payload.get("partial", "").strip()
                if partial_text and partial_text != self._last_partial_text:
                    self._last_partial_text = partial_text
                    if self.debug_audio:
                        print(f"[SPEECH][PARTIAL] {partial_text}")

        if partial_text:
            return RecognitionResult(text=partial_text, engine="vosk-partial")
        return None

    def _listen_with_google_via_sounddevice(self, timeout: int = 8) -> Optional[RecognitionResult]:
        sr = self._speech_recognition
        recognizer = self._sr_recognizer
        if sr is None or recognizer is None:
            return None

        print("[SPEECH] Đang nghe bằng Google SpeechRecognition qua sounddevice...")
        try:
            audio_bytes = self._record_phrase_with_sounddevice(timeout=timeout)
            if not audio_bytes:
                print("[SPEECH] Không thu được âm thanh đủ lớn để gửi lên Google.")
                return None

            audio_data = sr.AudioData(audio_bytes, self.sample_rate, 2)
            text = recognizer.recognize_google(audio_data, language="vi-VN")
            recognized = text.lower().strip()
            self._last_partial_text = recognized
            print(f"[SPEECH][GOOGLE] {recognized}")
            return RecognitionResult(text=recognized, engine="google-sounddevice")
        except sr.UnknownValueError:
            print("[SPEECH] Google chưa nhận ra nội dung câu nói.")
        except Exception as exc:  # pylint: disable=broad-except
            print(f"[SPEECH] Lỗi SpeechRecognition fallback: {exc}")
        return None

    def _record_phrase_with_sounddevice(self, timeout: int = 8) -> bytes:
        import sounddevice as sd  # type: ignore

        captured_chunks: list[bytes] = []
        speech_started = False
        started = time.time()
        last_voice_time = started

        def _callback(indata, frames, time_info, status) -> None:  # type: ignore
            del frames, time_info
            if status:
                print(f"[SPEECH][GOOGLE] Stream status: {status}")

            nonlocal speech_started, last_voice_time
            chunk = bytes(indata)
            rms = audioop.rms(chunk, 2)
            self._last_rms = rms
            if self.debug_audio:
                now = time.time()
                if now - self._last_debug_print > 1.0:
                    print(f"[MIC] RMS={rms} | backend=google-fallback")
                    self._last_debug_print = now

            if rms >= self.energy_threshold:
                if not speech_started:
                    print(f"[SPEECH] Phát hiện giọng nói, bắt đầu thu câu lệnh. RMS={rms}")
                speech_started = True
                last_voice_time = time.time()

            if speech_started:
                captured_chunks.append(chunk)

        with sd.RawInputStream(
            samplerate=self.sample_rate,
            blocksize=4000,
            dtype="int16",
            channels=1,
            callback=_callback,
        ):
            while time.time() - started < timeout:
                if speech_started and time.time() - last_voice_time > self.silence_timeout:
                    print("[SPEECH] Đã gặp khoảng lặng, kết thúc thu âm câu lệnh.")
                    break
                if speech_started and time.time() - started > self.max_phrase_seconds:
                    print("[SPEECH] Đã đạt thời lượng câu lệnh tối đa, dừng thu.")
                    break
                time.sleep(0.05)

        total_bytes = b"".join(captured_chunks)
        if self.debug_audio:
            duration = len(total_bytes) / (self.sample_rate * 2) if total_bytes else 0
            print(
                f"[SPEECH] Thu được {len(total_bytes)} bytes ~ {duration:.2f}s âm thanh, "
                f"RMS cuối={self._last_rms}"
            )
        return total_bytes
