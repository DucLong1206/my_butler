from __future__ import annotations

import datetime as dt
import os
import re
import time
import urllib.parse
import webbrowser
from dataclasses import dataclass
from typing import Optional

import requests

from tts import VietnameseTTS


@dataclass
class BrowserConfig:
    chrome_path: Optional[str] = os.getenv("CHROME_PATH")
    chrome_profile: Optional[str] = os.getenv("CHROME_PROFILE")


class CommandProcessor:
    def __init__(self, tts: VietnameseTTS) -> None:
        self.tts = tts
        self.browser_config = BrowserConfig()
        self.weather_api_key = os.getenv("OPENWEATHER_API_KEY", "")
        self.weather_city = os.getenv("WEATHER_CITY", "Hanoi")
        self.weather_lang = os.getenv("WEATHER_LANG", "vi")
        self.weather_units = os.getenv("WEATHER_UNITS", "metric")
        self.message_target = os.getenv("MESSAGE_TARGET", "messenger").lower()
        self._register_browser()

    def _register_browser(self) -> None:
        if not self.browser_config.chrome_path:
            return

        try:
            webbrowser.register(
                "chrome",
                None,
                webbrowser.BackgroundBrowser(self.browser_config.chrome_path),
            )
            print(f"[COMMAND] Đã đăng ký Chrome: {self.browser_config.chrome_path}")
        except Exception as exc:  # pylint: disable=broad-except
            print(f"[COMMAND] Không thể đăng ký Chrome: {exc}")

    def handle(self, command: str) -> str:
        text = self._normalize(command)
        print(f"[DEBUG] Xử lý lệnh: {text}")

        try:
            if self._is_music_command(text):
                return self._handle_music(text)
            if self._is_weather_command(text):
                return self._handle_weather()
            if self._is_time_command(text):
                return self._handle_time()
            if self._is_message_command(text):
                return self._handle_messages()
            if any(keyword in text for keyword in ("tạm biệt", "ngủ đi", "nghỉ đi")):
                return "Dạ vâng sếp, khi nào cần thì cứ gọi em là Long ơi hoặc Hey Long nhé."
            return (
                "Dạ sếp, em chưa hiểu lệnh này lắm. "
                "Hiện tại em hỗ trợ bật nhạc, xem thời tiết Hà Nội, xem giờ và kiểm tra tin nhắn."
            )
        except Exception as exc:  # pylint: disable=broad-except
            print(f"[ERROR] Lỗi xử lý lệnh: {exc}")
            return "Xin lỗi sếp, em xử lý lệnh chưa thành công. Sếp thử nói lại giúp em nhé."

    @staticmethod
    def _normalize(text: str) -> str:
        return " ".join(text.lower().strip().split())

    @staticmethod
    def _is_music_command(text: str) -> bool:
        return "nhạc" in text or "bài hát" in text or "mở nhạc" in text

    @staticmethod
    def _is_weather_command(text: str) -> bool:
        return any(keyword in text for keyword in ("bao nhiêu độ", "thời tiết", "nhiệt độ"))

    @staticmethod
    def _is_time_command(text: str) -> bool:
        return any(keyword in text for keyword in ("mấy giờ", "giờ rồi", "thời gian"))

    @staticmethod
    def _is_message_command(text: str) -> bool:
        return any(keyword in text for keyword in ("tin nhắn", "message", "messenger", "whatsapp", "zalo"))

    def _handle_music(self, text: str) -> str:
        query = self._extract_music_query(text)
        if not query:
            query = "nhạc thư giãn"

        search_url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(query)
        print(f"[COMMAND] Mở YouTube tìm kiếm: {search_url}")

        if self._try_open_first_youtube_result(query):
            return f"Dạ sếp, em đã mở bài nhạc đầu tiên cho từ khóa {query}."

        self._open_url(search_url)
        return f"Dạ sếp, em đã mở YouTube để tìm {query}. Sếp chọn bài đầu tiên giúp em nhé."

    def _extract_music_query(self, text: str) -> str:
        cleaned = text
        for prefix in ("bật nhạc", "mở nhạc", "nghe nhạc", "bài hát"):
            cleaned = cleaned.replace(prefix, "")
        return cleaned.strip(" ,.!?")

    def _try_open_first_youtube_result(self, query: str) -> bool:
        chrome_driver_path = os.getenv("CHROMEDRIVER_PATH")
        if not chrome_driver_path:
            print("[COMMAND] Không có CHROMEDRIVER_PATH, bỏ qua bước click tự động kết quả đầu tiên.")
            return False

        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.support.ui import WebDriverWait

            options = Options()
            options.add_argument("--start-maximized")
            options.add_argument("--disable-gpu")
            if self.browser_config.chrome_profile:
                options.add_argument(f"--user-data-dir={self.browser_config.chrome_profile}")
            if self.browser_config.chrome_path:
                options.binary_location = self.browser_config.chrome_path

            driver = webdriver.Chrome(service=Service(chrome_driver_path), options=options)
            url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(query)
            driver.get(url)
            first_video = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a#video-title"))
            )
            first_video.click()
            print("[COMMAND] Đã tự động mở kết quả YouTube đầu tiên.")
            return True
        except Exception as exc:  # pylint: disable=broad-except
            print(f"[COMMAND] Selenium không click được kết quả YouTube đầu tiên: {exc}")
            return False

    def _handle_weather(self) -> str:
        if not self.weather_api_key:
            return (
                "Dạ sếp, em chưa có API key OpenWeatherMap. "
                "Sếp thêm biến môi trường OPENWEATHER_API_KEY để em báo thời tiết Hà Nội chính xác hơn nhé."
            )

        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": self.weather_city,
            "appid": self.weather_api_key,
            "units": self.weather_units,
            "lang": self.weather_lang,
        }
        print(f"[COMMAND] Gọi weather API cho {self.weather_city}")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        payload = response.json()
        temp = round(payload["main"]["temp"])
        feels_like = round(payload["main"]["feels_like"])
        description = payload["weather"][0]["description"]
        humidity = payload["main"]["humidity"]
        return (
            f"Dạ sếp, thời tiết ở Hà Nội hiện tại khoảng {temp} độ C, "
            f"cảm giác như {feels_like} độ, trời {description}, độ ẩm {humidity} phần trăm."
        )

    def _handle_time(self) -> str:
        now = dt.datetime.now()
        return (
            f"Dạ sếp, bây giờ là {now.strftime('%H giờ %M phút')}, "
            f"ngày {now.strftime('%d/%m/%Y')}."
        )

    def _handle_messages(self) -> str:
        target = self.message_target
        if "whatsapp" in target:
            url = "https://web.whatsapp.com"
            unread = self._detect_unread_whatsapp(url)
            self._open_url(url)
            if unread is None:
                return (
                    "Dạ sếp, em đã mở WhatsApp Web. "
                    "Em chưa xác định chắc số tin chưa đọc, sếp xem nhanh trên màn hình giúp em nhé."
                )
            if unread > 0:
                return f"Dạ sếp, WhatsApp hiện có khoảng {unread} cuộc trò chuyện chưa đọc."
            return "Dạ sếp, em chưa thấy cuộc trò chuyện WhatsApp nào chưa đọc."

        url = "https://www.messenger.com"
        unread = self._detect_unread_messenger(url)
        self._open_url(url)
        if unread is None:
            return (
                "Dạ sếp, em đã mở Messenger Web. "
                "Nếu sếp đã đăng nhập sẵn thì có thể xem ngay, em chưa đọc được số thông báo chính xác."
            )
        if unread > 0:
            return f"Dạ sếp, Messenger đang có khoảng {unread} mục chưa đọc."
        return "Dạ sếp, em chưa thấy thông báo tin nhắn chưa đọc trên Messenger."

    def _detect_unread_messenger(self, url: str) -> Optional[int]:
        title = self._get_page_title(url)
        if not title:
            return None
        return self._extract_unread_from_title(title)

    def _detect_unread_whatsapp(self, url: str) -> Optional[int]:
        title = self._get_page_title(url)
        if title:
            unread = self._extract_unread_from_title(title)
            if unread is not None:
                return unread
        return None

    @staticmethod
    def _extract_unread_from_title(title: str) -> Optional[int]:
        matched = re.search(r"\((\d+)\)", title)
        if matched:
            return int(matched.group(1))
        return 0 if title else None

    def _get_page_title(self, url: str) -> Optional[str]:
        chrome_driver_path = os.getenv("CHROMEDRIVER_PATH")
        if not chrome_driver_path:
            print("[COMMAND] Không có CHROMEDRIVER_PATH, không thể đọc title trình duyệt tự động.")
            return None

        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service

            options = Options()
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
            options.add_argument("--log-level=3")
            if self.browser_config.chrome_profile:
                options.add_argument(f"--user-data-dir={self.browser_config.chrome_profile}")
            if self.browser_config.chrome_path:
                options.binary_location = self.browser_config.chrome_path

            driver = webdriver.Chrome(service=Service(chrome_driver_path), options=options)
            driver.get(url)
            time.sleep(5)
            title = driver.title
            driver.quit()
            print(f"[COMMAND] Title trang {url}: {title}")
            return title
        except Exception as exc:  # pylint: disable=broad-except
            print(f"[COMMAND] Không đọc được title trang {url}: {exc}")
            return None

    def _open_url(self, url: str) -> None:
        try:
            browser = webbrowser.get("chrome") if self.browser_config.chrome_path else webbrowser
            browser.open(url, new=2)
        except webbrowser.Error:
            webbrowser.open(url, new=2)
