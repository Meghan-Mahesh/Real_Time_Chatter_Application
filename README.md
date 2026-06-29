# 💬 Real-Time Chat Application

A full-stack **Real-Time Chat Application** built using **FastAPI**, **WebSocket**, **SQLAlchemy**, **SQLite**, and **Vanilla JavaScript**. The application enables multiple authenticated users to communicate instantly through WebSocket-based messaging while providing secure authentication, persistent chat history, automated content moderation, and an administrative dashboard.

---

## 🚀 Features

* 🔐 JWT-based User Authentication
* 👥 Real-time messaging using WebSockets
* 💾 Persistent chat history with SQLite
* ⚡ FastAPI REST APIs
* 🛡️ Automated content moderation with warning and blocking mechanism
* 👨‍💼 Admin Dashboard
* 📊 CSV export for users and messages
* 🔒 Password hashing using bcrypt
* 🎨 Responsive HTML, CSS, and JavaScript frontend

---

# 🛠 Tech Stack

### Backend

* Python
* FastAPI
* SQLAlchemy
* SQLite
* WebSocket
* Uvicorn

### Frontend

* HTML5
* CSS3
* JavaScript

### Authentication & Security

* JWT Authentication
* bcrypt Password Hashing

---

# 📁 Project Structure

```
Real_Time_Chatter_Application/
│
├── backend/
│   └── app/
│       ├── admin/
│       │   └── admin_routes.py
│       │
│       ├── auth/
│       │   ├── auth.py
│       │   └── jwt.py
│       │
│       ├── chat/
│       │   ├── websocket.py
│       │   └── messages.py
│       │
│       ├── ml/
│       │   └── bad_word_model.py
│       │
│       ├── utils/
│       │   └── security.py
│       │
│       ├── database.py
│       ├── main.py
│       ├── models.py
│       └── schemas.py
│
├── frontend/
│   ├── admin/
│   ├── assets/
│   ├── css/
│   ├── js/
│   ├── index.html
│   ├── register.html
│   └── chat.html
│
├── chat_app.db
├── requirements.txt
├── run.py
├── LICENSE
└── README.md
```

---

# 📂 File Overview

## Backend

### `run.py`

Application entry point that starts the FastAPI server using Uvicorn.

### `main.py`

Initializes the FastAPI application, configures middleware, registers API routes, and serves the frontend.

### `database.py`

Configures SQLite database connection, SQLAlchemy engine, session management, and dependency injection.

### `models.py`

Defines SQLAlchemy models for:

* User
* Message

### `schemas.py`

Contains Pydantic request and response schemas used for API validation.

---

## Authentication

### `auth.py`

Handles:

* User Registration
* User Login
* JWT Token Generation

### `jwt.py`

Responsible for:

* Creating JWT tokens
* Verifying tokens
* Authenticating users
* Admin authorization

---

## Chat Module

### `websocket.py`

Handles:

* WebSocket connections
* User authentication
* Message broadcasting
* Content moderation
* Database persistence

### `messages.py`

Provides REST API for loading previous chat history.

---

## ML Module

### `bad_word_model.py`

Implements automated content moderation.

Features:

* Detect prohibited words
* Track warnings
* Block repeated offenders

---

## Admin Module

### `admin_routes.py`

Provides APIs for:

* Admin Login
* Dashboard
* User Management
* Blocked Users
* Message Monitoring
* CSV Report Export

---

## Utilities

### `security.py`

Provides:

* Password Hashing
* Password Verification

---

# ▶️ Project Execution

## Step 1

Clone the repository.

```bash
git clone <repository-url>
```

Navigate into the project.

```bash
cd Real_Time_Chatter_Application
```

---

## Step 2

Create a virtual environment.

Windows

```bash
python -m venv .venv
```

Activate it.

Command Prompt

```bash
.venv\Scripts\activate
```

PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

---

## Step 3

Install all required dependencies.

```bash
pip install -r requirements.txt
```

---

## Step 4

Run the application.

```bash
python run.py
```

The backend starts on:

```
http://127.0.0.1:8000
```

---

# 👤 User Workflow

## Register

Create a new user by providing:

* Username
* Email
* Password

The password is securely hashed before storing in the database.

---

## Login

Login using:

* Email
* Password

A JWT token is generated and stored in the browser.

---

## Start Chatting

Once logged in:

* Previous chat history is loaded.
* A WebSocket connection is established automatically.
* Messages are delivered instantly to all connected users.

---

# 👥 Testing Multiple Users

To simulate real-time communication:

1. Open the application in one browser window.
2. Register/Login as **User A**.
3. Open the application again in an **Incognito Window** (or a different browser).
4. Register/Login as **User B**.
5. Send messages between both users.

Each browser maintains a separate authentication context, allowing simultaneous real-time messaging.

---

# 🛡 Content Moderation

The application includes an automated moderation system.

If a user sends prohibited language:

* First violation → Warning
* Second violation → Warning
* Third violation → User is automatically blocked

Blocked users cannot send further messages.

---

# 👨‍💼 Admin Features

The administrator can:

* Login securely
* View all users
* View blocked users
* Monitor chat messages
* Download Users CSV
* Download Messages CSV
* View dashboard statistics

---

# 🔄 Application Flow

```
Start Application

↓

Register User

↓

Login

↓

Generate JWT

↓

Open Chat

↓

Load Previous Messages

↓

Establish WebSocket Connection

↓

Send / Receive Messages

↓

Store Messages in Database

↓

Broadcast to Connected Users

↓

Admin Monitoring
```

---

# 🔐 Security Features

* JWT Authentication
* Password Hashing using bcrypt
* Role-Based Access Control
* WebSocket Authentication
* HTML Escaping to reduce XSS risk
* Automated User Blocking

---

# 📄 License

This project is licensed under the MIT License.
