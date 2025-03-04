document.addEventListener("DOMContentLoaded", function () {
  // === Gestion du modal pour les options sur une ligne ===
  function openRowOptions(rowData) {
    const modal = document.getElementById("rowOptionsModal");
    if (!modal) {
      console.error("Modal rowOptionsModal introuvable !");
      return;
    }
    const rowDetails = document.getElementById("rowDetails");
    rowDetails.textContent = `Pays: ${rowData.country} | Date: ${rowData.date} | Cas: ${rowData.cases} | Décès: ${rowData.deaths}`;
    modal.classList.remove("hidden");

    const btnUpdate = document.getElementById("btnUpdateRow");
    const btnDelete = document.getElementById("btnDeleteRow");
    const btnCancel = document.getElementById("btnCancelRow");

    if (!btnUpdate || !btnDelete || !btnCancel) {
      console.error("Un ou plusieurs boutons du modal ne sont pas trouvés.");
      return;
    }

    btnUpdate.onclick = function() {
      modal.classList.add("hidden");
      openUpdateModal(rowData);
    };

    btnDelete.onclick = function() {
      modal.classList.add("hidden");
      if (confirm("Confirmez-vous la suppression de cette donnée ?")) {
        const params = new URLSearchParams({
          country: rowData.country,
          date: rowData.date
        });
        fetch("http://127.0.0.1:8000/data/?" + params.toString(), {
          method: "DELETE"
        })
        .then(res => res.json())
        .then(result => {
          alert("Donnée supprimée avec succès !");
          location.reload();
        })
        .catch(err => {
          console.error("Erreur lors de la suppression :", err);
          alert("Erreur lors de la suppression !");
        });
      }
    };

    btnCancel.onclick = function() {
      modal.classList.add("hidden");
    };
  }

  // === Fonction pour ouvrir le modal de modification avec le formulaire pré-rempli ===
  function openUpdateModal(rowData) {
    const updateModal = document.getElementById("updateModal");
    if (!updateModal) {
      console.error("Modal updateModal introuvable !");
      return;
    }
    // Récupérer le formulaire du modal
    const updateFormModal = document.getElementById("updateFormModal");
    // Pré-remplir les champs
    updateFormModal.elements["country"].value = rowData.country;
    updateFormModal.elements["date"].value = rowData.date;
    updateFormModal.elements["cases"].value = rowData.cases;
    updateFormModal.elements["deaths"].value = rowData.deaths;
    updateFormModal.elements["recovered"].value = rowData.recovered;
    updateFormModal.elements["active"].value = rowData.active;
    updateFormModal.elements["latitude"].value = rowData.latitude || "";
    updateFormModal.elements["longitude"].value = rowData.longitude || "";
    updateFormModal.elements["who_region"].value = rowData.who_region || "";
    updateFormModal.elements["mortality_rate"].value = rowData.mortality_rate || "";
    updateFormModal.elements["recovery_rate"].value = rowData.recovery_rate || "";

    updateModal.classList.remove("hidden");

    // Gérer la soumission du formulaire dans le modal de mise à jour
    updateFormModal.onsubmit = function(e) {
      e.preventDefault();
      const formData = new FormData(this);
      const updatedData = Object.fromEntries(formData.entries());
      // Convertir les valeurs numériques
      updatedData.cases = parseInt(updatedData.cases);
      updatedData.deaths = parseInt(updatedData.deaths);
      updatedData.recovered = parseInt(updatedData.recovered);
      updatedData.active = parseInt(updatedData.active);
      if (updatedData.latitude) updatedData.latitude = parseFloat(updatedData.latitude);
      if (updatedData.longitude) updatedData.longitude = parseFloat(updatedData.longitude);
      if (updatedData.mortality_rate) updatedData.mortality_rate = parseFloat(updatedData.mortality_rate);
      if (updatedData.recovery_rate) updatedData.recovery_rate = parseFloat(updatedData.recovery_rate);

      fetch("http://127.0.0.1:8000/data/update/", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updatedData)
      })
      .then(res => res.json())
      .then(result => {
        alert("Donnée modifiée avec succès !");
        location.reload();
      })
      .catch(err => {
        console.error("Erreur lors de la modification :", err);
        alert("Erreur lors de la modification !");
      });
    };

  // Bouton Annuler
  const cancelBtn = document.getElementById("cancelUpdate");
  if (cancelBtn) {
    cancelBtn.onclick = function() {
      updateModal.classList.add("hidden");
    };
  } else {
    console.error("Le bouton 'cancelUpdate' est introuvable !");
  }
}

  // === Pagination et affichage du tableau ===
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
    fetch("http://127.0.0.1:8000/data/")
      .then(response => response.json())
      .then(data => {
        allData = data;
        if (allData.length === 0) {
          document.querySelector("#data-table tbody").innerHTML = "<tr><td colspan='11'>Aucune donnée disponible</td></tr>";
          return;
        }
        displayPage(1);
      })
      .catch(error => console.error("Erreur lors du chargement des données :", error));
  }

  function displayPage(page) {
    const tableBody = document.querySelector("#data-table tbody");
    tableBody.innerHTML = "";
    const start = (page - 1) * rowsPerPage;
    const end = start + rowsPerPage;
    const pageData = allData.slice(start, end);
    if (pageData.length === 0) {
      tableBody.innerHTML = "<tr><td colspan='11'>Aucune donnée disponible</td></tr>";
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
      `;
      tr.style.cursor = "pointer";
      tr.addEventListener("click", function() {
        openRowOptions(row);
      });
      tableBody.appendChild(tr);
    });
    const totalPages = Math.ceil(allData.length / rowsPerPage);
    document.querySelector("#pageInfo").textContent = `Page ${currentPage} / ${totalPages}`;
  }

  function waitForPaginationElements() {
    const prevBtn = document.querySelector("#prevPage");
    const nextBtn = document.querySelector("#nextPage");
    if (!prevBtn || !nextBtn) {
      setTimeout(waitForPaginationElements, 500);
      return;
    }
    prevBtn.addEventListener("click", () => {
      if (currentPage > 1) {
        currentPage--;
        displayPage(currentPage);
      }
    });
    nextBtn.addEventListener("click", () => {
      if (currentPage < Math.ceil(allData.length / rowsPerPage)) {
        currentPage++;
        displayPage(currentPage);
      }
    });
  }

  checkTableLoaded();
  waitForPaginationElements();

  // === Gestion du formulaire d'ajout (inchangé) ===
  document.getElementById("addForm").addEventListener("submit", function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    const data = Object.fromEntries(formData.entries());
    data.cases = parseInt(data.cases);
    data.deaths = parseInt(data.deaths);
    data.recovered = parseInt(data.recovered);
    data.active = parseInt(data.active);
    if (data.latitude) data.latitude = parseFloat(data.latitude);
    if (data.longitude) data.longitude = parseFloat(data.longitude);
    if (data.mortality_rate) data.mortality_rate = parseFloat(data.mortality_rate);
    if (data.recovery_rate) data.recovery_rate = parseFloat(data.recovery_rate);
  
    fetch("http://127.0.0.1:8000/data/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(result => {
      showPopup("Donnée ajoutée avec succès !", function() {
        location.reload();
      });
    })
    .catch(err => {
      console.error("Erreur lors de l'ajout :", err);
      showPopup("Erreur lors de l'ajout de la donnée !");
    });
  });
});
