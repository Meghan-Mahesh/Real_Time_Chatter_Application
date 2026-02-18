/* =========================
   AUTH CHECK
========================= */
const token = localStorage.getItem("token");
const username = localStorage.getItem("username");
const email = localStorage.getItem("email");

if (!token || !email) {
    window.location.href = "/";
}

/* =========================
   SET USERNAME
========================= */
if (username) {
    const userElem = document.getElementById("username");
    if (userElem) {
        userElem.innerText = username;
    }
}

/* =========================
   PROFILE PIC (EMAIL BASED)
========================= */
const profilePicKey = `profile_pic_${email}`;
const savedProfilePic = localStorage.getItem(profilePicKey);

if (savedProfilePic) {
    const img = document.getElementById("profile-pic");
    if (img) {
        img.src = savedProfilePic;
    }
}

/* =========================
   MESSAGE RENDER FUNCTION
========================= */
let lastSender = null;

function renderMessage(raw) {
    const box = document.getElementById("chat-box");
    const msgDiv = document.createElement("div");
    msgDiv.classList.add("message");

    const timePart = raw.match(/\[(.*?)\]/)?.[1] || "";
    const body = raw.replace(/\[.*?\]\s*/, "");

    const sender = body.split(":")[0];
    const text = body.split(":").slice(1).join(":").trim();

    const isMe = sender === username;
    msgDiv.classList.add(isMe ? "right" : "left");

    // Message grouping
    const showSender = sender !== lastSender && !isMe;
    lastSender = sender;

    msgDiv.innerHTML = `
        ${showSender ? `<div class="sender">${sender}</div>` : ""}
        <div class="text">${text}</div>
        <div class="time">${timePart.split(" ")[1] || ""}</div>
    `;

    box.appendChild(msgDiv);
    box.scrollTop = box.scrollHeight;
}

/* =========================
   LOAD CHAT HISTORY
========================= */
async function loadChatHistory() {
    try {
        const res = await fetch("/messages");
        if (!res.ok) return;

        const messages = await res.json();
        const box = document.getElementById("chat-box");
        box.innerHTML = "";
        lastSender = null;

        messages.forEach(msg => {
            const formatted = `[${msg.timestamp}] ${msg.user_name}: ${msg.message}`;
            renderMessage(formatted);
        });

    } catch (err) {
        console.error("History load failed:", err);
    }
}

/* =========================
   WEBSOCKET CONNECTION
========================= */
const ws = new WebSocket(`ws://127.0.0.1:8000/ws/${token}`);

ws.onopen = () => {
    console.log("Connected to server");
};

ws.onmessage = (event) => {
    renderMessage(event.data);
};

ws.onclose = () => {
    console.log("Disconnected from server");
};

ws.onerror = (err) => {
    console.error("WebSocket error:", err);
};

/* =========================
   SEND MESSAGE
========================= */
function sendMessage() {
    const msgInput = document.getElementById("message");
    const text = msgInput.value.trim();

    if (text && ws.readyState === WebSocket.OPEN) {
        ws.send(text);
        msgInput.value = "";
    }
}

/* =========================
   MENU TOGGLE
========================= */
function toggleMenu() {
    document.getElementById("side-menu").classList.toggle("open");
}

/* =========================
   PROFILE PIC UPLOAD
========================= */
document.getElementById("profile-pic-input").addEventListener("change", async function () {
    const file = this.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
        const res = await fetch(`/upload-profile-pic/${token}`, {
            method: "POST",
            body: formData
        });

        if (!res.ok) {
            alert("Profile image upload failed");
            return;
        }

        const data = await res.json();
        document.getElementById("profile-pic").src = data.profile_pic;

        // Persist using email
        localStorage.setItem(profilePicKey, data.profile_pic);

    } catch (err) {
        console.error("Upload error:", err);
    }
});

/* =========================
   LOGOUT
========================= */
function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    localStorage.removeItem("email");
    window.location.href = "/";
}

/* =========================
   CHANGE PASSWORD
========================= */
function openChangePassword() {
    document.getElementById("changePasswordModal").style.display = "flex";
}

function closeChangePassword() {
    document.getElementById("changePasswordModal").style.display = "none";
}

async function changePassword() {
    const oldPass = document.getElementById("oldPass").value;
    const newPass = document.getElementById("newPass").value;

    if (!oldPass || !newPass) {
        alert("Fill all fields");
        return;
    }

    const res = await fetch(`/change-password/${token}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            old_password: oldPass,
            new_password: newPass
        })
    });

    const data = await res.json();

    if (!res.ok) {
        alert(data.detail);
        return;
    }

    alert("Password updated successfully");
    closeChangePassword();
}

/* =========================
   INITIAL LOAD
========================= */
loadChatHistory();
