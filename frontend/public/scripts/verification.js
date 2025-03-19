document.addEventListener("DOMContentLoaded", () => {
  const token = localStorage.getItem("user_id");
  const logoutBtn = document.getElementById("logoutBtn");
  if (token && logoutBtn) {
    logoutBtn.style.display = "block";
  } else if (logoutBtn) {
    logoutBtn.style.display = "none";
  }
  
  if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
      console.log("Bouton de déconnexion cliqué");
      localStorage.removeItem("user_id");
      window.location.href = "index.html";
    });
  }

  if (!token) {
    window.location.href = "/";
  }
});
