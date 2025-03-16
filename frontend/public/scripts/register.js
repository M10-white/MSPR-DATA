document.addEventListener("DOMContentLoaded", () => {
    const registerForm = document.getElementById("registerForm");
    const errorMessage = document.getElementById("errorMessage");

    registerForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const formData = new FormData(registerForm);
        const data = Object.fromEntries(formData.entries());

        // Vérification de la confirmation du mot de passe
        if (data.password !== data.confirm_password) {
            errorMessage.textContent = "Les mots de passe ne correspondent pas.";
            return;
        }

        // Suppression de confirm_password avant d'envoyer à l'API
        delete data.confirm_password;

        try {
            const response = await fetch("http://127.0.0.1:5000/users/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                const result = await response.json();
                throw new Error(result.detail || "Erreur lors de l'inscription.");
            }

            const result = await response.json();
            console.log("Inscription réussie :", result);
            alert("Inscription réussie ! Vous pouvez maintenant vous connecter.");
            window.location.href = "index.html"; // Redirection vers la connexion

        } catch (error) {
            errorMessage.textContent = error.message;
        }
    });
});