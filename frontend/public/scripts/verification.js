document.addEventListener("DOMContentLoaded", () => {
    // Vérifie si un token d'accès est présent
    const token = localStorage.getItem("access_token");
    if (!token) {
      // Si le token n'est pas présent, redirige vers la page de connexion
      window.location.href = "/";
    }
  });