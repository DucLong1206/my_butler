const API_KEY = "AIzaSyD9ZmMWeV1HolZk1zXq3c6J7lPvaEAgxIk";
const SEARCH_ENDPOINT = "https://www.googleapis.com/youtube/v3/search";
const PLAYER_PAGE = "player.html";

const queryInput = document.getElementById("queryInput");
const searchButton = document.getElementById("searchButton");
const listenButton = document.getElementById("listenButton");
const statusEl = document.getElementById("status");
const resultEl = document.getElementById("result");
const videoTitleEl = document.getElementById("videoTitle");
const videoChannelEl = document.getElementById("videoChannel");
const videoLinkEl = document.getElementById("videoLink");
const playerStateEl = document.getElementById("playerState");
const controlButtons = document.querySelectorAll(".control-button");

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = SpeechRecognition ? new SpeechRecognition() : null;

let playerWindow = null;
let currentVideo = null;

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
    void handleCommand(transcript);
  };

  recognition.onerror = (event) => {
    const message = `Không nhận diện được giọng nói: ${event.error}`;
    updateStatus(message);
    speak(`Mình không nghe rõ lệnh. ${event.error}`);
  };
}

searchButton.addEventListener("click", () => {
  void handleCommand(queryInput.value);
});

queryInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    void handleCommand(queryInput.value);
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

controlButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const action = button.dataset.action;
    void executeControlAction(action);
  });
});

window.addEventListener("message", (event) => {
  if (event.origin !== window.location.origin) {
    return;
  }

  if (event.data?.type !== "PLAYER_STATUS") {
    return;
  }

  playerStateEl.textContent = event.data.message;
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

function parseControlCommand(rawCommand) {
  const command = rawCommand.toLowerCase().normalize("NFD").replace(/\p{Diacritic}/gu, "").trim();

  if (/^(tam dung|dung lai|pause|stop)$/.test(command) || command.includes("tam dung")) {
    return { action: "pause", message: "Đã nhận lệnh tạm dừng video." };
  }

  if (/^(phat|tiep tuc|play)$/.test(command) || command.includes("tiep tuc") || command.includes("phat video")) {
    return { action: "play", message: "Đã nhận lệnh phát video." };
  }

  if (command.includes("phong to") || command.includes("toan man hinh") || command.includes("fullscreen")) {
    return { action: "fullscreen", message: "Đã nhận lệnh phóng to video." };
  }

  if (command.includes("thu nho") || command.includes("nho lai") || command.includes("minimize")) {
    return { action: "shrink", message: "Đã nhận lệnh thu nhỏ player video." };
  }

  if (command.includes("2x") || command.includes("2 x") || command.includes("toc do 2") || command.includes("toc do hai")) {
    return { action: "speed-2", message: "Đã nhận lệnh chuyển tốc độ video sang 2x." };
  }

  if (command.includes("1x") || command.includes("1 x") || command.includes("toc do 1") || command.includes("toc do mot")) {
    return { action: "speed-1", message: "Đã nhận lệnh chuyển tốc độ video sang 1x." };
  }

  return null;
}

async function handleCommand(rawCommand) {
  const command = (rawCommand || "").trim();
  if (!command) {
    const message = "Bạn chưa nói hoặc nhập nội dung cần xử lý.";
    updateStatus(message);
    speak(message);
    return;
  }

  const control = parseControlCommand(command);
  if (control) {
    await executeControlAction(control.action, control.message);
    return;
  }

  updateStatus(`Đã nghe: "${command}". Đang tìm video phù hợp nhất...`);
  await openFirstVideo(command);
}

function ensurePlayerWindow() {
  if (!playerWindow || playerWindow.closed) {
    const message = "Bạn chưa mở video nào. Hãy tìm video trước rồi mới điều khiển được.";
    updateStatus(message);
    speak(message);
    return false;
  }

  return true;
}

async function executeControlAction(action, overrideMessage) {
  if (!ensurePlayerWindow()) {
    return;
  }

  const feedback = {
    play: "Đang phát video hiện tại.",
    pause: "Đã tạm dừng video hiện tại.",
    fullscreen: "Đang phóng to video hiện tại.",
    shrink: "Đang thu nhỏ player video.",
    "speed-1": "Đã chuyển tốc độ về 1x.",
    "speed-2": "Đã chuyển tốc độ sang 2x.",
  };

  playerWindow.focus();
  playerWindow.postMessage({ type: "PLAYER_COMMAND", action }, window.location.origin);
  const message = overrideMessage || feedback[action] || "Đã gửi lệnh điều khiển tới video hiện tại.";
  playerStateEl.textContent = message;
  updateStatus(message);
  speak(message);
}

function openPlayerWindow(videoId, title) {
  const playerUrl = new URL(PLAYER_PAGE, window.location.href);
  playerUrl.searchParams.set("videoId", videoId);
  playerUrl.searchParams.set("title", title);

  const features = "popup=yes,width=1280,height=840,left=120,top=80";
  if (!playerWindow || playerWindow.closed) {
    playerWindow = window.open(playerUrl.toString(), "my-butler-player", features);
  } else {
    playerWindow.location.href = playerUrl.toString();
    playerWindow.focus();
  }
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
    currentVideo = { videoId, title, channel };

    videoTitleEl.textContent = title;
    videoChannelEl.textContent = channel;
    videoLinkEl.href = videoUrl;
    playerStateEl.textContent = "Đang mở player điều khiển riêng...";
    resultEl.hidden = false;

    openPlayerWindow(videoId, title);

    const spokenMessage = `Đã tìm thấy video ${title} từ kênh ${channel}. Mình đang mở player để bạn điều khiển bằng giọng nói hoặc nút bấm.`;
    updateStatus(spokenMessage);
    speak(spokenMessage);
  } catch (error) {
    const message = `Không thể tìm video YouTube lúc này. ${error.message}`;
    updateStatus(message);
    speak(message);
  }
}
