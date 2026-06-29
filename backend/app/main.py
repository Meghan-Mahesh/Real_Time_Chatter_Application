from fastapi import FastAPI
from .database import engine
from .database import Base
from fastapi.middleware.cors import CORSMiddleware


# routers
from .auth.auth import router as auth_router
from .admin.admin_routes import router as admin_router
from .chat.websocket import router as chat_router
from .chat.messages import router as messages_router

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
FRONTEND_DIR = BASE_DIR / "frontend"
print(FRONTEND_DIR)

# ===============================
# CREATE TABLES
# ===============================
Base.metadata.create_all(bind=engine)

# ===============================
# FASTAPI APP
# ===============================
app = FastAPI(
    title="Real-Time Chat Application",
    description="Professional chat backend with admin, auth, ML moderation",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # frontend ke liye
    allow_credentials=True,
    allow_methods=["*"],   # POST, GET, OPTIONS sab allow
    allow_headers=["*"],
)
# ===============================
# INCLUDE ROUTERS
# ===============================
app.include_router(auth_router, prefix="/auth")
app.include_router(admin_router, prefix="/admin")
app.include_router(chat_router)
app.include_router(messages_router, prefix="/chat")

app.mount(
    "/",
    StaticFiles(directory=FRONTEND_DIR,html=True),
    name="frontend"
)

# ===============================
# ROOT
# ===============================
@app.get("/")
def home():
    return FileResponse(FRONTEND_DIR / "index.html")

