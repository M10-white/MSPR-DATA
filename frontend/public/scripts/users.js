document.addEventListener('DOMContentLoaded', async () => {
  // --- Chargement des composants principaux ---
  const componentsUsers = [
    { id: 'header', file: 'components/header.html' },
    { id: 'dashboard-users', file: 'components/dashboard-users.html' },
  ];

  for (const { id, file } of componentsUsers) {
    const response = await fetch(file);
    const html = await response.text();
    document.getElementById(id).innerHTML = html;
  }

  // --- Chargement des sous-composants du Dashboard Users ---
  const dashboardComponentsUsers = [
    { id: 'filter-bar', file: 'components/filter-barUsers.html' },
    { id: 'users-table', file: 'components/table-users.html' },
  ];

  for (const { id, file } of dashboardComponentsUsers) {
    const response = await fetch(file);
    const html = await response.text();
    const container = document.querySelector(`.${id}`);
    if (container) {
      container.innerHTML = html;
    }
  }

  console.log("✅ Tous les composants sont chargés !");
  console.log("🚀 Recherche du tableau...");

  let allUsers = []; // Stocke la liste complète des utilisateurs

  // --- Fonction pour récupérer et afficher les utilisateurs ---
  function fetchUsers() {
    fetch('http://127.0.0.1:5000/users/')
      .then(response => response.json())
      .then(data => {
        allUsers = data;
        displayUsers(allUsers);
      })
      .catch(error => console.error("Erreur lors de la récupération des utilisateurs :", error));
  }

  // --- Fonction pour afficher les utilisateurs dans le tableau ---
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
      `;document.addEventListener('DOMContentLoaded', async () => {
        // --- Chargement des composants principaux ---
        const componentsUsers = [
          { id: 'header', file: 'components/header.html' },
          { id: 'dashboard-users', file: 'components/dashboard-users.html' },
        ];
        for (const { id, file } of componentsUsers) {
          const response = await fetch(file);
          const html = await response.text();
          document.getElementById(id).innerHTML = html;
        }
        
        // --- Chargement des sous-composants du Dashboard Users ---
        const dashboardComponentsUsers = [
          { id: 'filter-bar', file: 'components/filter-barUsers.html' },
          { id: 'users-table', file: 'components/table-users.html' },
        ];
        for (const { id, file } of dashboardComponentsUsers) {
          const response = await fetch(file);
          const html = await response.text();
          const container = document.querySelector(`.${id}`);
          if (container) {
            container.innerHTML = html;
          }
        }
        
        console.log("✅ Tous les composants sont chargés !");
        console.log("🚀 Recherche du tableau...");
        
        let allUsers = []; // Stocke la liste complète des utilisateurs
        
        // --- Fonction pour récupérer et afficher les utilisateurs ---
        function fetchUsers() {
          fetch('http://127.0.0.1:5000/users/')
            .then(response => response.json())
            .then(data => {
              allUsers = data;
              displayUsers(allUsers);
            })
            .catch(error => console.error("Erreur lors de la récupération des utilisateurs :", error));
        }
        
        // --- Fonction pour afficher les utilisateurs dans le tableau ---
        function displayUsers(users) {
          const tbody = document.querySelector("#users-table tbody");
          tbody.innerHTML = "";
          if (users.length === 0) {
            tbody.innerHTML = "<tr><td colspan='5'>Aucun utilisateur trouvé</td></tr>";
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
            `;
            tr.style.cursor = "pointer";
            // Ouvrir la modal d'options lors du clic sur la ligne
            tr.addEventListener("click", () => {
              openUserOptionsModal(user);
            });
            tbody.appendChild(tr);
          });
        }
        
        // --- Fonction pour ouvrir la modal d'options sur une ligne utilisateur ---
        function openUserOptionsModal(user) {
          const modal = document.getElementById("userOptionsModal");
          if (!modal) {
            console.error("Modal userOptionsModal introuvable !");
            return;
          }
          const userDetails = document.getElementById("userDetails");
          userDetails.textContent = `ID: ${user.id} | Nom: ${user.username} | Email: ${user.email}`;
          modal.style.display = "flex";
          modal.classList.remove("hidden");
          setTimeout(() => {
            modal.classList.add("active");
          }, 10);
        
          const btnUpdate = document.getElementById("btnUpdateUser");
          const btnDelete = document.getElementById("btnDeleteUser");
          const btnCancel = document.getElementById("btnCancelUser");
          if (!btnUpdate || !btnDelete || !btnCancel) {
            console.error("Un ou plusieurs boutons du modal userOptionsModal sont introuvables.");
            return;
          }
        
          btnUpdate.onclick = () => {
            modal.classList.remove("active");
            setTimeout(() => {
              modal.classList.add("hidden");
              modal.style.display = "none";
              openUserUpdateModal(user);
            }, 300);
          };
        
          btnDelete.onclick = () => {
            modal.classList.remove("active");
            setTimeout(() => {
              modal.classList.add("hidden");
              modal.style.display = "none";
              openUserDeleteModal(user);
            }, 300);
          };
        
          btnCancel.onclick = () => {
            modal.classList.remove("active");
            setTimeout(() => {
              modal.classList.add("hidden");
              modal.style.display = "none";
            }, 300);
          };
        }
        
        // --- Fonction pour ouvrir le modal de modification d'un utilisateur ---
        function openUserUpdateModal(userData) {
          const updateModal = document.getElementById("updateUserModal");
          if (!updateModal) {
            console.error("Modal updateUserModal introuvable !");
            return;
          }
          const updateForm = document.getElementById("updateUserFormModal");
          if (!updateForm) {
            console.error("Formulaire updateUserFormModal introuvable !");
            return;
          }
          // Pré-remplissage des champs
          updateForm.elements["id"].value = userData.id;
          updateForm.elements["username"].value = userData.username;
          updateForm.elements["email"].value = userData.email;
          updateForm.elements["password"].value = userData.password;
        
          updateModal.style.display = "flex";
          updateModal.classList.remove("hidden");
          setTimeout(() => {
            updateModal.classList.add("active");
          }, 10);
        
          updateForm.onsubmit = async (e) => {
            e.preventDefault();
            const formData = new FormData(updateForm);
            const updatedUser = Object.fromEntries(formData.entries());
            try {
              const response = await fetch(`http://127.0.0.1:5000/users/${userData.id}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(updatedUser)
              });
              if (!response.ok) throw new Error(await response.text());
              alert("✅ Utilisateur modifié avec succès !");
              updateModal.classList.remove("active");
              setTimeout(() => {
                updateModal.classList.add("hidden");
                updateModal.style.display = "none";
              }, 300);
              fetchUsers();
            } catch (err) {
              console.error("🚨 Erreur lors de la modification :", err);
              alert("⚠️ Échec de la modification !");
            }
          };
        
          const cancelUpdateBtn = document.getElementById("cancelUserUpdate");
          if (cancelUpdateBtn) {
            cancelUpdateBtn.onclick = () => {
              updateModal.classList.remove("active");
              setTimeout(() => {
                updateModal.classList.add("hidden");
                updateModal.style.display = "none";
              }, 300);
            };
          } else {
            console.error("Bouton cancelUserUpdate introuvable !");
          }
        }
        
        // --- Fonction pour ouvrir le modal de suppression d'un utilisateur ---
        function openUserDeleteModal(userData) {
          const deleteModal = document.getElementById("deleteUserModal");
          if (!deleteModal) {
            console.error("Modal deleteUserModal introuvable !");
            return;
          }
          const deleteDetails = document.getElementById("deleteUserDetails");
          deleteDetails.textContent = `Voulez-vous vraiment supprimer l'utilisateur ${userData.username} ?`;
          deleteModal.style.display = "flex";
          deleteModal.classList.remove("hidden");
          setTimeout(() => {
            deleteModal.classList.add("active");
          }, 10);
        
          const confirmDeleteBtn = document.getElementById("confirmUserDelete");
          const cancelDeleteBtn = document.getElementById("cancelUserDelete");
        
          if (confirmDeleteBtn) {
            confirmDeleteBtn.onclick = async () => {
              try {
                const response = await fetch(`http://127.0.0.1:5000/users/${userData.id}`, {
                  method: "DELETE"
                });
                if (!response.ok) throw new Error(await response.text());
                alert("✅ Utilisateur supprimé avec succès !");
                deleteModal.classList.remove("active");
                setTimeout(() => {
                  deleteModal.classList.add("hidden");
                  deleteModal.style.display = "none";
                }, 300);
                fetchUsers();
              } catch (err) {
                console.error("🚨 Erreur lors de la suppression :", err);
                alert("⚠️ Échec de la suppression !");
              }
            };
          }
          if (cancelDeleteBtn) {
            cancelDeleteBtn.onclick = () => {
              deleteModal.classList.remove("active");
              setTimeout(() => {
                deleteModal.classList.add("hidden");
                deleteModal.style.display = "none";
              }, 300);
            };
          }
        }
        
        // --- Gestion du formulaire d'ajout ---
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
            alert("✅ Utilisateur ajouté avec succès !");
            addUserForm.reset();
            fetchUsers();
          })
          .catch(error => console.error("Erreur lors de l'ajout :", error));
        });
        
        // Charger la liste des utilisateurs au démarrage
        fetchUsers();
      });
      
      // Rendre toute la ligne cliquable pour afficher les options
      tr.style.cursor = "pointer";
      tr.addEventListener("click", () => {
        openUserOptionsModal(user);
      });
      tbody.appendChild(tr);
    });
  }

  // --- Fonction pour ouvrir le modal d'options sur une ligne utilisateur ---
  function openUserOptionsModal(userData) {
    const modal = document.getElementById("userOptionsModal");
    if (!modal) {
      console.error("Modal userOptionsModal introuvable !");
      return;
    }
    const detailsElem = document.getElementById("userDetails");
    detailsElem.textContent = `ID: ${userData.id} | Nom: ${userData.username} | Email: ${userData.email}`;
    
    // Afficher le modal
    modal.style.display = "flex";
    modal.classList.remove("hidden");
    setTimeout(() => {
      modal.classList.add("active");
    }, 10);
    
    // Boutons d'options
    const btnUpdate = document.getElementById("btnUpdateUser");
    const btnDelete = document.getElementById("btnDeleteUser");
    const btnCancel = document.getElementById("btnCancelUser");
    
    if (!btnUpdate || !btnDelete || !btnCancel) {
      console.error("Un ou plusieurs boutons du modal userOptionsModal ne sont pas trouvés.");
      return;
    }
    
    // Pour éviter les accumulations d'écouteurs, on affecte onclick directement
    btnUpdate.onclick = () => {
      modal.classList.remove("active");
      setTimeout(() => {
        modal.classList.add("hidden");
        openUserUpdateModal(userData);
      }, 300);
    };
    
    btnDelete.onclick = () => {
      modal.classList.remove("active");
      setTimeout(() => {
        modal.classList.add("hidden");
        openUserDeleteModal(userData);
      }, 300);
    };
    
    btnCancel.onclick = () => {
      modal.classList.remove("active");
      setTimeout(() => {
        modal.classList.add("hidden");
        modal.style.display = "none";
      }, 300);
    };
  }

  // --- Fonction pour ouvrir le modal de modification d'un utilisateur ---
  function openUserUpdateModal(userData) {
    const updateModal = document.getElementById("updateUserModal");
    if (!updateModal) {
      console.error("Modal updateUserModal introuvable !");
      return;
    }
    const updateFormModal = document.getElementById("updateUserFormModal");
    if (!updateFormModal) {
      console.error("Le formulaire updateUserFormModal est introuvable !");
      return;
    }
    
    // Pré-remplissage du formulaire avec les données actuelles
    updateFormModal.elements["id"].value = userData.id;
    updateFormModal.elements["username"].value = userData.username;
    updateFormModal.elements["email"].value = userData.email;
    updateFormModal.elements["password"].value = userData.password;
    
    updateModal.style.display = "flex";
    updateModal.classList.remove("hidden");
    setTimeout(() => {
      updateModal.classList.add("active");
    }, 10);
    
    updateFormModal.onsubmit = async (e) => {
      e.preventDefault();
      const formData = new FormData(updateFormModal);
      const updatedUser = Object.fromEntries(formData.entries());
      
      try {
        const response = await fetch(`http://127.0.0.1:5000/users/${userData.id}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(updatedUser)
        });
        if (!response.ok) throw new Error(await response.text());
        alert("✅ Utilisateur modifié avec succès !");
        updateModal.classList.remove("active");
        setTimeout(() => {
          updateModal.classList.add("hidden");
          updateModal.style.display = "none";
        }, 300);
        fetchUsers();
      } catch (err) {
        console.error("🚨 Erreur lors de la modification :", err);
        alert("⚠️ Échec de la modification !");
      }
    };

    const cancelBtn = document.getElementById("cancelUserUpdate");
    if (cancelBtn) {
      cancelBtn.onclick = () => {
        updateModal.classList.remove("active");
        setTimeout(() => {
          updateModal.classList.add("hidden");
          updateModal.style.display = "none";
        }, 300);
      };
    } else {
      console.error("Le bouton 'cancelUserUpdate' est introuvable !");
    }
  }

  // --- Fonction pour ouvrir le modal de suppression d'un utilisateur ---
  function openUserDeleteModal(userData) {
    const deleteModal = document.getElementById("deleteUserModal");
    if (!deleteModal) {
      console.error("Modal deleteUserModal introuvable !");
      return;
    }
    const detailsElem = document.getElementById("deleteUserDetails");
    detailsElem.textContent = `Voulez-vous vraiment supprimer l'utilisateur ${userData.username} ?`;
    
    deleteModal.style.display = "flex";
    deleteModal.classList.remove("hidden");
    setTimeout(() => {
      deleteModal.classList.add("active");
    }, 10);
    
    const confirmDeleteBtn = document.getElementById("confirmUserDelete");
    const cancelDeleteBtn = document.getElementById("cancelUserDelete");
    
    if (confirmDeleteBtn) {
      confirmDeleteBtn.onclick = async () => {
        try {
          const response = await fetch(`http://127.0.0.1:5000/users/${userData.id}`, {
            method: "DELETE"
          });
          if (!response.ok) throw new Error(await response.text());
          alert("✅ Utilisateur supprimé avec succès !");
          deleteModal.classList.remove("active");
          setTimeout(() => {
            deleteModal.classList.add("hidden");
            deleteModal.style.display = "none";
          }, 300);
          fetchUsers();
        } catch (err) {
          console.error("🚨 Erreur lors de la suppression :", err);
          alert("⚠️ Échec de la suppression !");
        }
      };
    }
    if (cancelDeleteBtn) {
      cancelDeleteBtn.onclick = () => {
        deleteModal.classList.remove("active");
        setTimeout(() => {
          deleteModal.classList.add("hidden");
          deleteModal.style.display = "none";
        }, 300);
      };
    }
  }

  // --- Gestion du formulaire d'ajout ---
  const addUserForm = document.getElementById("addUserForm");
  addUserForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const formData = new FormData(addUserForm);
    const newUser = Object.fromEntries(formData.entries());
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
      alert("✅ Utilisateur ajouté avec succès !");
      addUserForm.reset();
      fetchUsers();
    })
    .catch(error => console.error("Erreur lors de l'ajout :", error));
  });

  // Charger la liste des utilisateurs au démarrage
  fetchUsers();
});
