from __future__ import annotations

import re
import signal
import time
from typing import Optional

from commands import CommandProcessor
from speech import SpeechListener
from tts import VietnameseTTS

WAKE_WORD_PATTERNS = (
    r"\blong\s*ơi\b",
    r"\blong\s*oi\b",
    r"\bhey\s+long\b",
    r"^\s*long\b",
)
LISTEN_TIMEOUT_SECONDS = 8
IDLE_SLEEP_SECONDS = 0.15


def normalize_text(text: str) -> str:
    return " ".join(text.lower().strip().split())


def contains_wake_word(text: str) -> bool:
    normalized = normalize_text(text)
    return any(re.search(pattern, normalized) for pattern in WAKE_WORD_PATTERNS)


def strip_wake_word(text: str) -> str:
    normalized = normalize_text(text)
    for pattern in WAKE_WORD_PATTERNS:
        matched = re.search(pattern, normalized)
        if matched:
            return normalized[matched.end() :].strip(" ,.!?-")
    return normalized


def main() -> int:
    print("[SYSTEM] Khởi động trợ lý giọng nói cho sếp...")
    print("[SYSTEM] Wake word hỗ trợ: Long ơi / long oi / Hey Long / Long")
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
                speech.print_debug_snapshot(prefix="[MIC][IDLE]")
                time.sleep(IDLE_SLEEP_SECONDS)
                continue

            print(f"[HEARD] {heard_text}")
            if not contains_wake_word(heard_text):
                print("[DEBUG] Có âm thanh nhưng chưa thấy wake word, tiếp tục chờ.")
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
