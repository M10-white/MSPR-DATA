document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("loginForm");
    const errorMessage = document.getElementById("errorMessage");

    if (!loginForm) {
        console.error("Formulaire de connexion introuvable !");
        return;
    }

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

            console.log("Réponse brute :", response); // 👀 Ajout pour voir la réponse HTTP

            if (!response.ok) {
                const errorResponse = await response.json();
                throw new Error(errorResponse.detail || "Email ou mot de passe incorrect");
            }

            const result = await response.json();
            console.log("Connexion réussie :", result);

            if (!result.user_id || !result.username) {
                throw new Error("Données de réponse invalides.");
            }

            sessionStorage.setItem("user_id", result.user_id);
            console.log("Vérification sessionStorage:", sessionStorage.getItem("user_id"));            
            localStorage.setItem("username", result.username);
            console.log("Utilisateur connecté : ID =", result.user_id);

            // Stockage en cookie en plus pour éviter la perte de user_id
            document.cookie = `user_id=${result.user_id}; path=/; max-age=86400`;

            window.location.href = "menu.html";
        } catch (error) {
            console.error("Erreur de connexion :", error);
            if (errorMessage) {
                errorMessage.textContent = error.message;
                errorMessage.style.color = "red";
            }
        }
    });
});
