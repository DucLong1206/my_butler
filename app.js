const API_KEY = "AIzaSyD9ZmMWeV1HolZk1zXq3c6J7lPvaEAgxIk";
const SEARCH_ENDPOINT = "https://www.googleapis.com/youtube/v3/search";

const queryInput = document.getElementById("queryInput");
const searchButton = document.getElementById("searchButton");
const listenButton = document.getElementById("listenButton");
const statusEl = document.getElementById("status");
const resultEl = document.getElementById("result");
const videoTitleEl = document.getElementById("videoTitle");
const videoChannelEl = document.getElementById("videoChannel");
const videoLinkEl = document.getElementById("videoLink");

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = SpeechRecognition ? new SpeechRecognition() : null;

if (recognition) {
  recognition.lang = "vi-VN";
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  recognition.onstart = () => {
    updateStatus("Đang nghe lệnh của bạn...");
  };

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript.trim();
    queryInput.value = transcript;
    updateStatus(`Đã nghe: \"${transcript}\". Đang tìm video phù hợp nhất...`);
    void openFirstVideo(transcript);
  };

  recognition.onerror = (event) => {
    speak(`Mình không nghe rõ lệnh. Lỗi: ${event.error}`);
    updateStatus(`Không nhận diện được giọng nói: ${event.error}`);
  };
}

searchButton.addEventListener("click", () => {
  void openFirstVideo(queryInput.value);
});

queryInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    void openFirstVideo(queryInput.value);
  }
});

listenButton.addEventListener("click", () => {
  if (!recognition) {
    const message = "Trình duyệt này chưa hỗ trợ nhận diện giọng nói. Bạn hãy nhập lệnh bằng bàn phím.";
    updateStatus(message);
    speak(message);
    return;
  }

  recognition.start();
});

function normalizeQuery(query) {
  return query
    .replace(/^(mở|mo|bật|bat|tìm|tim|play)\s+/i, "")
    .replace(/^(video|bài hát|bai hat|nhạc|nhac)\s+/i, "")
    .trim();
}

function speak(text) {
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = "vi-VN";
  utterance.rate = 1;
  utterance.pitch = 1;
  window.speechSynthesis.speak(utterance);
}

function updateStatus(message) {
  statusEl.textContent = message;
}

async function openFirstVideo(query) {
  const cleanedQuery = normalizeQuery(query || "");

  if (!cleanedQuery) {
    const message = "Bạn chưa nói hoặc nhập nội dung cần tìm trên YouTube.";
    updateStatus(message);
    speak(message);
    return;
  }

  updateStatus(`Đang tìm video chính xác nhất cho: ${cleanedQuery}`);

  const url = new URL(SEARCH_ENDPOINT);
  url.search = new URLSearchParams({
    part: "snippet",
    q: cleanedQuery,
    maxResults: "1",
    type: "video",
    order: "relevance",
    regionCode: "VN",
    relevanceLanguage: "vi",
    key: API_KEY,
  }).toString();

  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    const firstItem = data.items?.[0];

    if (!firstItem?.id?.videoId) {
      const message = `Mình chưa tìm thấy video phù hợp cho ${cleanedQuery}.`;
      updateStatus(message);
      speak(message);
      return;
    }

    const videoId = firstItem.id.videoId;
    const title = firstItem.snippet?.title || "Không có tiêu đề";
    const channel = firstItem.snippet?.channelTitle || "Không rõ kênh";
    const videoUrl = `https://www.youtube.com/watch?v=${videoId}`;

    videoTitleEl.textContent = title;
    videoChannelEl.textContent = channel;
    videoLinkEl.href = videoUrl;
    resultEl.hidden = false;

    const spokenMessage = `Đã tìm thấy video ${title} từ kênh ${channel}. Mình sẽ mở YouTube cho bạn ngay bây giờ.`;
    updateStatus(spokenMessage);
    speak(spokenMessage);

    window.open(videoUrl, "_blank", "noopener,noreferrer");
  } catch (error) {
    const message = `Không thể tìm video YouTube lúc này. ${error.message}`;
    updateStatus(message);
    speak(message);
  }
}
