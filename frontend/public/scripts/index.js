document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("loginForm");
    const errorMessage = document.getElementById("errorMessage");
  
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const formData = new FormData(loginForm);
      const data = Object.fromEntries(formData.entries());
  
      try {
        const response = await fetch("http://127.0.0.1:5000/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data)
        });
        if (!response.ok) {
          throw new Error("Email ou mot de passe incorrect");
        }
        const result = await response.json();
        console.log("Connexion OK :", result);
        localStorage.setItem("access_token", result.access_token);
        window.location.href = "menu.html";
      } catch (error) {
        errorMessage.textContent = error.message;
      }
    });
  });
  