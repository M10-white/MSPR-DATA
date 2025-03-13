document.addEventListener('DOMContentLoaded', async () => {
    const componentsUsers = [
        { id: 'header', file: 'components/header.html' },
        { id: 'dashboard-users', file: 'components/dashboard-users.html' },
    ];
    

    for (const { id, file } of componentsUsers) {
        const response = await fetch(file);
        const html = await response.text();
        document.getElementById(id).innerHTML = html;
    }

    // Charge les sous-composants du Dashboard
    const dashboardComponentsUsers = [
       // { id: 'filter-bar', file: 'components/filter-barUsers.html' },
        { id: 'users-table', file: 'components/table-users.html' },
    ];
    

    for (const { id, file } of dashboardComponentsUsers) {
        const response = await fetch(file);
        const html = await response.text();
        const container = document.querySelector(`.${id}`);

        if (container) {
            container.innerHTML = html;
        } // else {
        //     console.error(`🚨 Impossible de trouver l'élément .${id} dans le DOM`);
        // }
    }

    console.log("✅ Tous les composants sont chargés !");
    console.log("🚀 Recherche du tableau...");

    let allUsers = []; // Stocke la liste complète des utilisateurs
  
    // Fonction pour récupérer et afficher les utilisateurs
    function fetchUsers() {
      fetch('http://127.0.0.1:5000/users/')
        .then(response => response.json())
        .then(data => {
          allUsers = data;
          displayUsers(allUsers);
        })
        .catch(error => console.error("Erreur lors de la récupération des utilisateurs :", error));
    }
  
    // Fonction pour afficher les utilisateurs dans le tableau
    function displayUsers(users) {
      const tbody = document.querySelector("#users-table tbody");
      tbody.innerHTML = "";
      if (users.length === 0) {
        tbody.innerHTML = "<tr><td colspan='6'>Aucun utilisateur trouvé</td></tr>";
        return;
      }
  
      users.forEach(user => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${user.id}</td>
          <td>${user.username}</td>
          <td>${user.email}</td>
          <td>${user.password}</td>
          <td>${user.created_at ? new Date(user.created_at).toLocaleString() : 'N/A'}</td>
          <td>
            <button class="edit-btn" data-id="${user.id}">Modifier</button>
            <button class="delete-btn" data-id="${user.id}">Supprimer</button>
          </td>
        `;
        // Rendre la ligne cliquable pour des actions ou juste les boutons selon vos préférences
        tbody.appendChild(tr);
      });
  
      // Attacher les écouteurs aux boutons de suppression et d'édition
      document.querySelectorAll(".delete-btn").forEach(btn => {
        btn.addEventListener("click", () => {
          const userId = btn.getAttribute("data-id");
          deleteUser(userId);
        });
      });
  
      document.querySelectorAll(".edit-btn").forEach(btn => {
        btn.addEventListener("click", () => {
          const userId = btn.getAttribute("data-id");
          editUserPrompt(userId);
        });
      });
    }
  
    // Fonction pour supprimer un utilisateur
    function deleteUser(userId) {
      if (confirm("Confirmez-vous la suppression de cet utilisateur ?")) {
        fetch(`http://127.0.0.1:5000/users/${userId}`, {
          method: "DELETE"
        })
        .then(response => {
          if (!response.ok) {
            throw new Error("Erreur lors de la suppression");
          }
          return response.json();
        })
        .then(result => {
          alert("Utilisateur supprimé avec succès !");
          fetchUsers(); // Recharge la liste
        })
        .catch(error => console.error("Erreur lors de la suppression :", error));
      }
    }
  
    // Fonction pour modifier un utilisateur via prompt (peut être remplacée par un modal)
    function editUserPrompt(userId) {
      // Récupère l'utilisateur à modifier
      fetch(`http://127.0.0.1:5000/users/${userId}`)
        .then(response => response.json())
        .then(user => {
          const newUsername = prompt("Nouveau nom d'utilisateur :", user.username);
          if (newUsername === null) return; // Annulation
          const newEmail = prompt("Nouvel email :", user.email);
          if (newEmail === null) return;
          const newPassword = prompt("Nouveau mot de passe :", user.password);
          if (newPassword === null) return;
  
          const updatedUser = {
            username: newUsername,
            email: newEmail,
            password: newPassword,
            created_at: user.created_at // Conserver la date de création
          };
  
          updateUser(userId, updatedUser);
        })
        .catch(error => console.error("Erreur lors de la récupération de l'utilisateur :", error));
    }
  
    // Fonction pour mettre à jour un utilisateur
    function updateUser(userId, updatedUser) {
      fetch(`http://127.0.0.1:5000/users/${userId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updatedUser)
      })
      .then(response => {
        if (!response.ok) {
          throw new Error("Erreur lors de la modification");
        }
        return response.json();
      })
      .then(result => {
        alert("Utilisateur modifié avec succès !");
        fetchUsers(); // Recharge la liste
      })
      .catch(error => console.error("Erreur lors de la modification :", error));
    }
  
    // Gestion du formulaire d'ajout
    const addUserForm = document.getElementById("addUserForm");
    addUserForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const formData = new FormData(addUserForm);
      const newUser = Object.fromEntries(formData.entries());
      // Note : En production, pensez à hasher le mot de passe côté serveur.
      fetch("http://127.0.0.1:5000/users/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newUser)
      })
      .then(response => {
        if (!response.ok) {
          throw new Error("Erreur lors de l'ajout");
        }
        return response.json();
      })
      .then(result => {
        alert("Utilisateur ajouté avec succès !");
        addUserForm.reset();
        fetchUsers();
      })
      .catch(error => console.error("Erreur lors de l'ajout :", error));
    });
  
    // Charger la liste des utilisateurs au démarrage
    fetchUsers();
  });
  