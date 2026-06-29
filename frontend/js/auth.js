/* =========================================================
	AUTH LOGIC (LOGIN + REGISTER)
========================================================= */

/* ---------- LOGIN ---------- */
async function loginUser () {
	const email = document.getElementById("email").value.trim();
	const password = document.getElementById("password").value.trim();
	const errorBox = document.getElementById("error");

	errorBox.innerText = "";

	if (!email || !password) {
		errorBox.innerText = "Please fill all fields";
		return;
	}

	try {
		const response = await fetch(
			CONFIG.BASE_URL + CONFIG.endpoints.login,
			{
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ email, password })
			}
		);

		const data = await response.json();

		if (!response.ok) {
			errorBox.innerText = data.detail || "Invalid credentials";
			return;
		}

		// save JWT
		localStorage.setItem("token", data.access_token);

		// extract user id from token payload
		const payload = JSON.parse(atob(data.access_token.split(".")[1]));
		localStorage.setItem("user_id", payload.user_id);
		localStorage.setItem("username", payload.username);

		window.location.href = "chat.html";

	} catch (err) {
		errorBox.innerText = "Server not reachable";
	}
}

/* ---------- REGISTER ---------- */
async function registerUser () {
	const username = document.getElementById("username").value.trim();
	const email = document.getElementById("email").value.trim();
	const password = document.getElementById("password").value.trim();
	const errorBox = document.getElementById("error");

	errorBox.innerText = "";

	if (!username || !email || !password) {
		errorBox.innerText = "All fields are required";
		return;
	}

	try {
		const response = await fetch(
			CONFIG.BASE_URL + CONFIG.endpoints.register,
			{
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ username, email, password })
			}
		);

		const data = await response.json();

		if (!response.ok) {
			errorBox.innerText = data.detail || "Registration failed";
			return;
		}

		// success → login page
		window.location.href = "index.html";

	} catch (err) {
		errorBox.innerText = "Server error";
	}
}
