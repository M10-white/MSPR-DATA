document.addEventListener("DOMContentLoaded", () => {
  const token = localStorage.getItem("acess_token");
  const logoutBtn = document.getElementById("logoutBtn");
  if (token && logoutBtn) {
    logoutBtn.style.display = "block";
  } else if (logoutBtn) {
    logoutBtn.style.display = "none";
  }
  
  if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
      console.log("Bouton de déconnexion cliqué");
      localStorage.removeItem("acess_token");
      window.location.href = "index.html";
    });
  }

  if (!token) {
    window.location.href = "/";
  }
});
