const userId = localStorage.getItem("user_id");
if (!userId) {
  window.location.href = "/login.html"; // Redirection si pas connecté
}


document.addEventListener("DOMContentLoaded", function () {
  // === Gestion du modal pour les options sur une ligne ===
  function openRowOptions(rowData) {
    const modal = document.getElementById("modalOptions");
    modal.querySelector(".modal-body").textContent = `Pays: ${rowData.country} | Date: ${rowData.date} | Cas: ${rowData.cases} | Décès: ${rowData.deaths}`;
    modal.classList.remove("hidden");

    const btnUpdate = document.getElementById("btnUpdateRow");
    const btnDelete = document.getElementById("btnDeleteRow");
    const btnCancel = document.getElementById("btnCancel");

    btnUpdate.onclick = function() {
      modal.classList.add("hidden");
      openUpdateModal(rowData);
    };

    btnDelete.onclick = function() {
      modal.classList.add("hidden");
      if (confirm("Confirmez-vous la suppression de cette donnée ?")) {
        fetch(`http://127.0.0.1:5000/data/${userId}/${rowData.id}`, {
          method: "DELETE"
        })
        .then(() => {
          alert("Donnée supprimée avec succès !");
          location.reload();
        })
        .catch(err => {
          console.error("Erreur lors de la suppression :", err);
          alert("Erreur lors de la suppression !");
        });
    };

    btnCancel.onclick = function() {
      modal.classList.add("hidden");
    };
  }

  // Bouton Annuler
  const cancelBtn = document.getElementById("cancelUpdate");
  if (cancelBtn) {
    cancelBtn.onclick = function() {
      document.getElementById("updateModal").classList.add("hidden");
    };
  }

  // === Chargement des données ===
  let allData = [];
  let currentPage = 1;
  const rowsPerPage = 10;

  function checkTableLoaded() {
    const tableBody = document.querySelector("#data-table tbody");
    if (!tableBody) {
      setTimeout(checkTableLoaded, 500);
      return;
    }
    loadTableData();
  }

  function loadTableData() {
    fetch(`http://127.0.0.1:5000/data/${userId}`)
      .then(res => res.json())
      .then(data => {
        allData = data;
        displayPage(1);
      })
      .catch(error => console.error("Erreur lors du chargement des données :", error));
  }


  function displayPage(page) {
    const tableBody = document.querySelector("#data-table tbody");
    tableBody.innerHTML = "";  

    const start = (page - 1) * rowsPerPage;
    const end = start + rowsPerPage;
    const pageData = filteredData.slice(start, end);

    if (pageData.length === 0) {
        tableBody.innerHTML = "<tr><td colspan='12'>Aucune donnée disponible</td></tr>";
        return;
    }

    pageData.forEach(row => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${row.country}</td>
            <td>${row.date}</td>
            <td>${row.cases}</td>
            <td>${row.deaths}</td>
            <td>${row.recovered}</td>
            <td>${row.active}</td>
            <td>${row.latitude ?? "N/A"}</td>
            <td>${row.longitude ?? "N/A"}</td>
            <td>${row.who_region ?? "N/A"}</td>
            <td>${row.mortality_rate ?? "N/A"}%</td>
            <td>${row.recovery_rate ?? "N/A"}%</td>
            <td>
                <button class="btn-modifier" data-id="${row.id}">Modifier</button>
                <button class="btn-supprimer" data-id="${row.id}">Supprimer</button>
            </td>
        `;

        tableBody.appendChild(tr);
    });

    // 🔥 Attendre que les boutons existent avant d'ajouter les événements
    setTimeout(() => {
        document.querySelectorAll(".btn-modifier").forEach(btn => {
            btn.addEventListener("click", (e) => {
                e.stopPropagation();
                const rowId = btn.getAttribute("data-id");
                const rowData = filteredData.find(r => r.id == rowId);
                if (rowData) openUpdateModal(rowData);
            });
        });

        document.querySelectorAll(".btn-supprimer").forEach(btn => {
            btn.addEventListener("click", (e) => {
                e.stopPropagation();
                const rowId = btn.getAttribute("data-id");
                if (confirm("Confirmez-vous la suppression de cette donnée ?")) {
                    fetch(`http://127.0.0.1:5000/data/${userId}/${rowId}`, {
                        method: "DELETE"
                    })
                    .then(() => {
                        alert("Donnée supprimée avec succès !");
                        loadTableData();
                    })
                    .catch(err => {
                        console.error("Erreur lors de la suppression :", err);
                        alert("Erreur lors de la suppression !");
                    });
                }
            });
        });

        console.log("✅ Boutons ajoutés et événements attachés !");
    }, 500);
}


  document.getElementById("prevPage").onclick = function() {
    if (currentPage > 1) {
      currentPage--;
      displayPage(currentPage);
    };
  }

  document.getElementById("nextPage").onclick = function() {
    if (currentPage * rowsPerPage < allData.length) {
      currentPage++;
      displayPage(currentPage);
    }
  };

  checkTableLoaded();
}
});
