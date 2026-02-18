# Real_Time_Chatter_Application
To create a high-quality GitHub **README.md**, you need a balance of technical detail, clear instructions, and a professional layout. Since this is for a **REAL TIME CHATTER APPLICATION**, highlighting the real-time nature of the project is key.

Below is the complete content for your `README.md`. You can copy this directly into your file.

---

# # REAL TIME CHATTER APPLICATION 💬

A modern, high-performance real-time messaging platform built with **FastAPI**, **WebSockets**, and **SQLModel**. This application features secure user authentication, persistent chat history, and a responsive, interactive user interface.

---

## 🚀 Features

* **Real-Time Messaging:** Instant message delivery using full-duplex WebSocket communication.
* **Persistent Chat History:** Messages are stored in an SQLite database and retrieved upon login.
* **Secure Authentication:** Password hashing using **Bcrypt** and session management via **UUID tokens**.
* **Profile Customization:** Users can upload profile pictures and update passwords securely.
* **Responsive UI:** A mobile-friendly design featuring a sliding side-menu and smooth message animations.
* **Session Persistence:** LocalStorage integration to keep users logged in across refreshes.

---

## 🛠️ Tech Stack

* **Backend:** [FastAPI](https://fastapi.tiangolo.com/) (Python)
* **Database & ORM:** [SQLModel](https://sqlmodel.tiangolo.com/) & SQLite
* **Security:** Passlib (Bcrypt)
* **Frontend:** HTML5, CSS3 (Flexbox), Vanilla JavaScript
* **Server:** Uvicorn (ASGI)

---

## 📂 Project Structure

```text
app/
├── static/                 # Frontend assets (HTML, CSS, JS)
│   ├── uploads/            # User-uploaded images
│   ├── chat.html           # Main chat UI
│   ├── login.html          # Authentication entry
│   ├── register.html       # Signup page
│   ├── chat.js             # Client-side logic
│   └── style.css           # Styling & Animations
├── server.py               # Application entry & API routes
├── auth.py                 # Hashing & Security logic
├── database.py             # Database session management
├── models.py               # SQLModel table definitions
├── websocket_manager.py    # Real-time connection handler
└── project.db              # SQLite database file

```

---

## ⚙️ Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/real-time-chatter.git
cd real-time-chatter

```

### 2. Install dependencies

Ensure you have Python 3.9+ installed, then run:

```bash
pip install fastapi uvicorn sqlmodel passlib[bcrypt] python-multipart

```

### 3. Run the Application

Start the server using Uvicorn:

```bash
uvicorn app.server:app --reload

```

### 4. Access the App

Open your browser and navigate to:
`http://127.0.0.1:8000`

---

## 🔄 User Workflow

1. **Registration:** New users create an account; passwords are encrypted immediately.
2. **Login:** Validated users receive a unique UUID token.
3. **Chat Interface:** The system establishes a WebSocket connection using the token.
4. **History:** The server pushes existing chat history from the database to the client.
5. **Live Chat:** Messages are sent, saved to the database, and broadcasted to all active users simultaneously.

---

## 🔒 Security

* **Zero Plain-Text Passwords:** All credentials undergo Bcrypt salting and hashing.
* **Token Isolation:** WebSocket connections require a valid UUID token from the `ActiveUsers` table to prevent unauthorized access.
* **Data Integrity:** SQLModel provides strict type-checking and validation for all incoming API data.

---
