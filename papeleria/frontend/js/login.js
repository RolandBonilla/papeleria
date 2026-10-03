document.getElementById("login-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const session = await api("/auth/login", {
      method: "POST",
      body: { username: document.getElementById("username").value, password: document.getElementById("password").value },
    });
    localStorage.setItem("session", JSON.stringify(session));
    location.href = "index.html";
  } catch (error) { showMessage(error.message, "error"); }
});
