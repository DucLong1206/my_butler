from __future__ import annotations

import os
import signal
import sys
import time
from typing import Optional

from commands import CommandProcessor
from speech import SpeechListener
from tts import VietnameseTTS

WAKE_WORDS = ("long ơi", "hey long", "long oi")
LISTEN_TIMEOUT_SECONDS = 8
IDLE_SLEEP_SECONDS = 0.15


def normalize_text(text: str) -> str:
    return " ".join(text.lower().strip().split())


def contains_wake_word(text: str) -> bool:
    normalized = normalize_text(text)
    return any(keyword in normalized for keyword in WAKE_WORDS)


def strip_wake_word(text: str) -> str:
    normalized = normalize_text(text)
    for keyword in WAKE_WORDS:
        if keyword in normalized:
            cleaned = normalized.replace(keyword, "", 1).strip(" ,.!?-")
            return cleaned
    return normalized


def main() -> int:
    print("[SYSTEM] Khởi động trợ lý giọng nói cho sếp...")
    print("[SYSTEM] Wake word: Long ơi / Hey Long")
    print("[SYSTEM] Nhấn Ctrl+C để thoát.\n")

    tts = VietnameseTTS(rate=175, volume=1.0)
    speech = SpeechListener()
    commands = CommandProcessor(tts=tts)
    running = True

    def _handle_exit(signum: int, _frame: Optional[object]) -> None:
        nonlocal running
        print(f"\n[SYSTEM] Nhận tín hiệu dừng ({signum}). Đang tắt trợ lý...")
        running = False

    signal.signal(signal.SIGINT, _handle_exit)
    signal.signal(signal.SIGTERM, _handle_exit)

    tts.speak("Chào sếp, em đã sẵn sàng lắng nghe.")

    while running:
        try:
            heard_text = speech.listen_for_text(timeout=LISTEN_TIMEOUT_SECONDS)
            if not heard_text:
                time.sleep(IDLE_SLEEP_SECONDS)
                continue

            print(f"[HEARD] {heard_text}")
            if not contains_wake_word(heard_text):
                print("[DEBUG] Không có wake word, bỏ qua để tiết kiệm tài nguyên.")
                time.sleep(IDLE_SLEEP_SECONDS)
                continue

            command_text = strip_wake_word(heard_text)
            if not command_text:
                tts.speak("Dạ sếp, em đang nghe đây ạ.")
                continue

            print(f"[COMMAND] {command_text}")
            reply = commands.handle(command_text)
            if reply:
                tts.speak(reply)

            time.sleep(IDLE_SLEEP_SECONDS)
        except KeyboardInterrupt:
            running = False
        except Exception as exc:  # pylint: disable=broad-except
            print(f"[ERROR] Lỗi vòng lặp chính: {exc}")
            tts.speak("Xin lỗi sếp, em vừa gặp chút trục trặc nhưng vẫn đang cố gắng chạy tiếp.")
            time.sleep(1)

    print("[SYSTEM] Trợ lý đã dừng.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
