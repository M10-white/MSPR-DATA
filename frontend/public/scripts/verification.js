document.addEventListener("DOMContentLoaded", () => {
  const token = localStorage.getItem("access_token");
  const logoutBtn = document.getElementById("logoutBtn");

  if (token && logoutBtn) {
    // Affiche le bouton de déconnexion
    logoutBtn.style.display = "block";
  }

  if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
      // Supprimer le token et rediriger vers la page de connexion
      localStorage.removeItem("access_token");
      window.location.href = "index.html";
    });
  }

  if (!token) {
    window.location.href = "/";
  }
});