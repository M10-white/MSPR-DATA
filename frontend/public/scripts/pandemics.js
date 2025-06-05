document.addEventListener("DOMContentLoaded", async () => {
  // Fonction simple pour afficher un message (ici avec alert)
  function showPopup(message, callback) {
    alert(message);
    if (callback) callback();
  }

  const componentsPandemics = [
    { id: 'header', file: 'components/header.html' },
    { id: 'dashboard-pandemics', file: 'components/dashboard-pandemics.html' },
  ];

  for (const { id, file } of componentsPandemics) {
    const response = await fetch(file);
    const html = await response.text();
    document.getElementById(id).innerHTML = html;
  }

  const dashboardComponentsPandemics = [
    { id: 'filter-bar', file: 'components/filter-barPandemics.html' },
    { id: 'data-table', file: 'components/table-pandemics.html' },
  ];

  for (const { id, file } of dashboardComponentsPandemics) {
    const response = await fetch(file);
    const html = await response.text();
    const container = document.querySelector(`.${id}`);
    if (container) {
      container.innerHTML = html;
    }
  }

  console.log("✅ Tous les composants sont chargés !");
  console.log("🚀 Recherche du tableau...");

  // --- Gestion du modal pour les options sur une ligne ---
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
        // Utilise l'identifiant unique (rowData.id) pour la suppression
        fetch(`http://127.0.0.1:5000/data/${rowData.id}`, {
          method: "DELETE"
        })
        .then(res => res.json())
        .then(result => {
          alert("Donnée supprimée avec succès !");
          fetchTableData();
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

  // --- Fonction pour charger les données avec anti-cache ---
  function fetchTableData() {
    // Ajout d'un timestamp pour éviter le cache
    fetch(`http://127.0.0.1:5000/data/1?ts=${Date.now()}`)
      .then(response => response.json())
      .then(data => {
        allData = data.sort((a, b) => b.id - a.id);
        filteredData = allData;
        if (!Array.isArray(allData)) {
          console.error("La réponse n'est pas un tableau :", allData);
          return;
        }
        if (allData.length === 0) {
          document.querySelector("#data-table tbody").innerHTML = "<tr><td colspan='11'>Aucune donnée disponible</td></tr>";
          return;
        }
        currentPage = 1;
        displayPage(1);
      })
      .catch(error => console.error("Erreur lors du chargement des données :", error));
  }

  // --- Fonction pour ouvrir le modal de modification ---
  function openUpdateModal(rowData) {
    const updateModal = document.getElementById("updateModal");
    if (!updateModal) {
      console.error("Modal updateModal introuvable !");
      return;
    }
    const updateFormModal = document.getElementById("updateFormModal");
    if (!updateFormModal) {
      console.error("Le formulaire updateFormModal est introuvable !");
      return;
    }
    
    // Pré-remplissage des champs avec gestion pour afficher 0 correctement
    updateFormModal.elements["country"].value = rowData.country;
    updateFormModal.elements["date"].value = rowData.date;
    updateFormModal.elements["cases"].value = rowData.cases;
    updateFormModal.elements["deaths"].value = rowData.deaths;
    updateFormModal.elements["recovered"].value = rowData.recovered;
    updateFormModal.elements["active"].value = rowData.active;
    updateFormModal.elements["latitude"].value = (rowData.latitude !== null && rowData.latitude !== undefined) ? rowData.latitude : "";
    updateFormModal.elements["longitude"].value = (rowData.longitude !== null && rowData.longitude !== undefined) ? rowData.longitude : "";
    updateFormModal.elements["who_region"].value = rowData.who_region ? rowData.who_region : "";
    updateFormModal.elements["mortality_rate"].value = (rowData.mortality_rate === 0 || rowData.mortality_rate) ? rowData.mortality_rate : "";
    updateFormModal.elements["recovery_rate"].value = (rowData.recovery_rate === 0 || rowData.recovery_rate) ? rowData.recovery_rate : "";
    
    // Affichage du modal
    updateModal.style.display = "flex";
    updateModal.classList.remove("hidden");
    setTimeout(() => {
      updateModal.classList.add("active");
    }, 10);
    
    updateFormModal.onsubmit = async (e) => {
      e.preventDefault();
      const formData = new FormData(updateFormModal);
      const updatedData = Object.fromEntries(formData.entries());
      
      // Conversion des valeurs numériques et gestion des champs vides
      updatedData.cases = parseInt(updatedData.cases);
      updatedData.deaths = parseInt(updatedData.deaths);
      updatedData.recovered = parseInt(updatedData.recovered);
      updatedData.active = parseInt(updatedData.active);
      updatedData.latitude = updatedData.latitude.trim() === "" ? null : parseFloat(updatedData.latitude);
      updatedData.longitude = updatedData.longitude.trim() === "" ? null : parseFloat(updatedData.longitude);
      updatedData.mortality_rate = updatedData.mortality_rate.trim() === "" ? 0 : parseFloat(updatedData.mortality_rate);
      updatedData.recovery_rate = updatedData.recovery_rate.trim() === "" ? 0 : parseFloat(updatedData.recovery_rate);
      
      // Récupération de l'user_id
      const userId = sessionStorage.getItem("user_id");
      const normalizedDate = new Date(rowData.date).toISOString().substring(0, 10);
      const url = `http://127.0.0.1:5000/data/${userId}/${rowData.country}/${normalizedDate}`;
      
      try {
        const response = await fetch(url, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(updatedData)
        });
        if (!response.ok) throw new Error(await response.text());
        alert("✅ Donnée mise à jour !");
        updateModal.classList.remove("active");
        setTimeout(() => {
          updateModal.classList.add("hidden");
          updateModal.style.display = "none";
        }, 300);
        fetchTableData();
      } catch (err) {
        console.error("🚨 Erreur lors de la modification :", err);
        alert("⚠️ Échec de la modification !");
      }
    };
    
    const cancelBtn = document.getElementById("cancelUpdate");
    if (cancelBtn) {
      cancelBtn.addEventListener("click", () => {
        console.log("❌ Annulation de la modification");
        updateModal.classList.remove("active");
        setTimeout(() => {
          updateModal.classList.add("hidden");
          updateModal.style.display = "none";
        }, 300);
      });
    } else {
      console.error("Le bouton 'cancelUpdate' est introuvable !");
    }
  }

  // --- Pagination et affichage du tableau ---
  let allData = [];
  let currentPage = 1;
  const rowsPerPage = 10;

  // Récupérer les données pour un user_id fixe (ici 1)
  function fetchTableData() {
    fetch("http://127.0.0.1:5000/data/1")
      .then(response => response.json())
      .then(data => {
        allData = data.sort((a, b) => b.id - a.id);
        filteredData = allData;
        if (!Array.isArray(allData)) {
          console.error("La réponse n'est pas un tableau :", allData);
          return;
        }
        if (allData.length === 0) {
          document.querySelector("#data-table tbody").innerHTML = "<tr><td colspan='11'>Aucune donnée disponible</td></tr>";
          return;
        }
        currentPage = 1;
        displayPage(1);
      })
      .catch(error => console.error("Erreur lors du chargement des données :", error));
  }

  function displayPage(page) {
    const tableBody = document.querySelector("#data-table tbody");
    tableBody.innerHTML = "";
    const start = (page - 1) * rowsPerPage;
    const end = start + rowsPerPage;
    // IMPORTANT : utiliser filteredData pour afficher les données filtrées
    const pageData = filteredData.slice(start, end);
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
        <td>${typeof row.mortality_rate === "number" ? row.mortality_rate.toFixed(3) : "N/A"}%</td>
        <td>${typeof row.recovery_rate === "number" ? row.recovery_rate.toFixed(3) : "N/A"}%</td>
      `;
      tr.style.cursor = "pointer";
      tr.addEventListener("click", function() {
        openRowOptions(row);
      });
      tableBody.appendChild(tr);
    });
    const totalPages = Math.ceil(filteredData.length / rowsPerPage);
    const pageInfo = document.querySelector("#pageInfo");
    if (pageInfo) {
      pageInfo.textContent = `Page ${currentPage} / ${totalPages}`;
    }
    const prevBtn = document.querySelector("#prevPage");
    const nextBtn = document.querySelector("#nextPage");
    if (prevBtn) {
      prevBtn.style.display = currentPage === 1 ? "none" : "block";
    }
    if (nextBtn) {
      nextBtn.style.display = currentPage === totalPages ? "none" : "block";
    }
  }

  fetchTableData();

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
      if (currentPage < Math.ceil(filteredData.length / rowsPerPage)) {
        currentPage++;
        displayPage(currentPage);
      }
    });
  }
  waitForPaginationElements();

  function applyFilters() {
    const countryFilter = document.getElementById("country").value.trim().toLowerCase();
    const omsFilter = document.getElementById("omsRegion").value.trim().toLowerCase();
    const dateFilter = document.getElementById("date").value;
  
    console.log("Filtres appliqués :", countryFilter, omsFilter, dateFilter);
  
    filteredData = allData.filter(row => {
      let match = true;
      if (countryFilter !== "") {
        match = match && row.country.toLowerCase().trim().includes(countryFilter);
      }
      if (omsFilter !== "") {
        match = match && row.who_region && row.who_region.toLowerCase().trim().includes(omsFilter);
      }
      if (dateFilter) {
        const rowDate = new Date(row.date).toISOString().substring(0, 10);
        match = match && rowDate === dateFilter;
      }
      return match;
    });
  
    console.log("Données filtrées :", filteredData);
    currentPage = 1;
    displayPage(currentPage);
  }
  
  function waitForFilterElements() {
    const countryInput = document.getElementById("country");
    const omsInput = document.getElementById("omsRegion");
    const dateInput = document.getElementById("date");
  
    if (!countryInput || !omsInput || !dateInput) {
      console.warn("⏳ Éléments de filtre non encore disponibles, nouvelle tentative...");
      setTimeout(waitForFilterElements, 500);
      return;
    }
  
    countryInput.addEventListener("input", () => {
      console.log("Valeur du filtre pays :", countryInput.value);
      applyFilters();
    });
    omsInput.addEventListener("input", () => {
      console.log("Valeur du filtre région OMS :", omsInput.value);
      applyFilters();
    });
    dateInput.addEventListener("change", () => {
      console.log("Valeur du filtre date :", dateInput.value);
      applyFilters();
    });
  }
  waitForFilterElements();
  
  // --- Gestion du formulaire d'ajout ---
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
  
    fetch("http://127.0.0.1:5000/data/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(result => {
      showPopup("Donnée ajoutée avec succès !", function() {
        fetchTableData();
      });
    })
    .catch(err => {
      console.error("Erreur lors de l'ajout :", err);
      showPopup("Erreur lors de l'ajout de la donnée !");
    });
  });
});
