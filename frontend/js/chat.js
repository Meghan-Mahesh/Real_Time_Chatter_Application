// ===============================
// AUTH CHECK
// ===============================
const token = localStorage.getItem("token");
if (!token) window.location.href = "index.html";

const payload = JSON.parse(atob(token.split(".")[1]));
const myUsername = payload.username || "Me";

let lastMessageDate = null;
let isBlocked = false;

// ===============================
// LOAD OLD MESSAGES
// ===============================
async function loadOldMessages() {
  const res = await fetch(CONFIG.BASE_URL + "/chat/messages", {
    headers: {
      Authorization: "Bearer " + token
    }
  });

  const messages = await res.json();
  messages.forEach(renderMessage);
}

// ===============================
// CONNECT SOCKET
// ===============================
let socket = null;

function connectSocket() {
  socket = new WebSocket(
    CONFIG.WS_URL + CONFIG.endpoints.chatSocket + "?token=" + token
  );

  socket.onopen = () => {
    console.log("✅ WebSocket connected");
  };

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);

    // 🛑 Detect block message
    if (data.alert) {
      alert(data.text);
      return; // message bubble me render mat karo
    }

    // 🚫 Block detect
    if (data.blocked) {
      isBlocked = true;
      alert(data.text);
      return;
    }

    renderMessage(data);
  };

  socket.onclose = () => {
    console.log("❌ WebSocket disconnected");

    if (isBlocked) {
      localStorage.clear();
      alert("You have been blocked.");
      window.location.href = "index.html";
    }
  };

  socket.onerror = (err) => {
    console.error("WebSocket error:", err);
  };
}

// ===============================
// SEND MESSAGE
// ===============================
function sendMessage() {
  const input = document.getElementById("messageInput");
  const text = input.value.trim();
  if (!text || socket.readyState !== WebSocket.OPEN) return;

  socket.send(
    JSON.stringify({
      text: text
    })
  );

  input.value = "";
}

// ===============================
// RENDER MESSAGE
// ===============================
function renderMessage(data) {
  if (!data.timestamp) {
    data.timestamp = new Date().toISOString();
  }

  const container = document.getElementById("messages");

  // ⚡ Fixed: Parse timestamp as UTC to avoid Today/Yesterday mismatch
  const messageDate = new Date(data.timestamp + "Z");
  const today = new Date();

  const messageDay = messageDate.toDateString();
  const todayDay = today.toDateString();

  const yesterday = new Date();
  yesterday.setDate(today.getDate() - 1);
  const yesterdayDay = yesterday.toDateString();

  let displayDate = "";

  if (messageDay === todayDay) {
    displayDate = "Today";
  } else if (messageDay === yesterdayDay) {
    displayDate = "Yesterday";
  } else {
    displayDate = messageDate.toLocaleDateString();
  }

  if (lastMessageDate !== messageDay) {
    const separator = document.createElement("div");
    separator.className = "date-separator";
    separator.innerText = displayDate;
    container.appendChild(separator);

    lastMessageDate = messageDay;
  }

  const div = document.createElement("div");
  const isMine = data.user === myUsername;

  div.className = "message " + (isMine ? "mine" : "theirs");

  div.innerHTML = `
    <div class="msg-sender">
      ${isMine ? "You" : escapeHtml(data.user)}
    </div>
    <div class="msg-content">${escapeHtml(data.text)}</div>
    <div class="msg-time">${formatTime(data.timestamp)}</div>
  `;

  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

// ===============================
// UTILS
// ===============================
function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function formatTime(ts) {
  if (!ts) return "";
  // ⚡ Fixed: Parse as UTC to match server time
  return new Date(ts + "Z").toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit"
  });
}

// ===============================
// LOGOUT
// ===============================
function logout() {
  if (socket) socket.close();
  localStorage.clear();
  window.location.href = "index.html";
}

// ===============================
// INIT
// ===============================
window.onload = () => {
  loadOldMessages();   // 👈 pehle old chat
  connectSocket();     // 👈 phir real-time

  document
    .getElementById("messageInput")
    .addEventListener("keydown", (e) => {
      if (e.key === "Enter") sendMessage();
    });
};
