/* =========================================================
   GLOBAL CONFIG
   Backend: FastAPI @ http://127.0.0.1:8000
========================================================= */

const CONFIG = {
  BASE_URL: "http://127.0.0.1:8000",
  WS_URL: "ws://127.0.0.1:8000",

  endpoints: {
    // user auth
    login: "/auth/login",
    register: "/auth/register",

    // chat websocket
    chatSocket: "/chat/ws",

    // admin (already aligned)
    adminLogin: "/admin/login",
    adminDashboard: "/admin/dashboard"
  }
}
