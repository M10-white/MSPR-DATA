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

    // Pour éviter les accumulations d'écouteurs, nous utilisons directement onclick
    btnUpdate.onclick = function() {
      modal.classList.add("hidden");
      // Par simplicité, nous utilisons prompt pour modifier le nombre de cas
      const newCases = prompt("Modifier le nombre de cas :", rowData.cases);
      if (newCases !== null) {
        rowData.cases = parseInt(newCases);
        fetch("http://127.0.0.1:8000/data/update/", {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(rowData)
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
      }
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

  // === Pagination et affichage du tableau ===
  let allData = [];
  let currentPage = 1;
  const rowsPerPage = 20;

  function checkTableLoaded() {
    const tableBody = document.querySelector("#data-table tbody");
    if (!tableBody) {
      console.warn("⏳ Tableau non encore disponible, nouvelle tentative...");
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
      // Rendre la ligne cliquable pour ouvrir le modal d'options
      tr.style.cursor = "pointer";
      tr.addEventListener("click", function() {
        openRowOptions(row);
      });
      tableBody.appendChild(tr);
    });
    const totalPages = Math.ceil(allData.length / rowsPerPage);
    document.querySelector("#pageInfo").textContent = `Page ${currentPage} / ${totalPages}`;
    document.querySelector("#prevPage").disabled = currentPage === 1;
    document.querySelector("#nextPage").disabled = currentPage === totalPages;
  }

  document.querySelector("#prevPage").addEventListener("click", () => {
    if (currentPage > 1) {
      currentPage--;
      displayPage(currentPage);
    }
  });

  document.querySelector("#nextPage").addEventListener("click", () => {
    if (currentPage < Math.ceil(allData.length / rowsPerPage)) {
      currentPage++;
      displayPage(currentPage);
    }
  });

  checkTableLoaded();

  // === Gestion du formulaire d'ajout (reste inchangé) ===
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
