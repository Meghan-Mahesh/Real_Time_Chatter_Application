// ---------- Admin Login ----------
async function adminLogin() {
  const email = document.getElementById("adminEmail").value;
  const password = document.getElementById("adminPassword").value;
  const errorBox = document.getElementById("adminError");

  errorBox.innerText = "";

  try {
    const res = await fetch(CONFIG.BASE_URL + CONFIG.endpoints.adminLogin, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });

    const data = await res.json();

    if (!res.ok) {
      errorBox.innerText = data.detail || "Login failed";
      return;
    }

    localStorage.setItem("admin_token", data.access_token);
    window.location.href = "admin_dashboard.html";

  } catch {
    errorBox.innerText = "Server not reachable";
  }
}

// ---------- Dashboard ----------
async function loadDashboard() {
  const token = localStorage.getItem("admin_token");
  if (!token) {
    window.location.href = "admin_login.html";
    return;
  }

  const res = await fetch(CONFIG.BASE_URL + CONFIG.endpoints.adminDashboard, {
    headers: {
      Authorization: "Bearer " + token
    }
  });

  const data = await res.json();

  document.getElementById("totalUsers").innerText = data.total_users;
  document.getElementById("totalMessages").innerText = data.total_messages;
  document.getElementById("blockedUsers").innerText = data.blocked_users;

  const table = document.getElementById("messageTable");
  table.innerHTML = "";

  data.messages.forEach(m => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${m.username}</td>
      <td>${m.message}</td>
      <td>${m.time}</td>
      <td>${m.blocked ? "🚫 Blocked" : "✅ OK"}</td>
    `;
    table.appendChild(row);
  });
}

// ---------- CSV Download ----------
function downloadCSV(type="users") {
  const token = localStorage.getItem("admin_token");
  if (!token) return;

  let endpoint = type === "messages" ? "/admin/download/messages" : "/admin/download/users";

  fetch(CONFIG.BASE_URL + endpoint, {
    headers: { Authorization: "Bearer " + token }
  })
  .then(res => res.blob())
  .then(blob => {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = type === "messages" ? "messages.csv" : "users.csv";
    a.click();
  });
}



// ---------- Logout ----------
function adminLogout() {
  localStorage.removeItem("admin_token");
  window.location.href = "admin_login.html";
}

// Auto-load
if (window.location.pathname.includes("admin_dashboard")) {
  loadDashboard();
}
