document.addEventListener("DOMContentLoaded", function () {
    console.log("🚀 Script chargé, recherche du tableau...");

    // Variables pour la pagination
    let allData = [];         // Stocke toutes les données récupérées
    let filteredData = [];    // Stocke les données filtrées après application des filtres
    let currentPage = 1;
    const rowsPerPage = 10;   // Nombre de lignes à afficher par page

    // Vérifie que le tableau est présent
    function checkTableLoaded() {
        const tableBody = document.querySelector("#data-table tbody");
        if (!tableBody) {
            console.warn("⏳ Tableau non encore disponible, nouvelle tentative...");
            setTimeout(checkTableLoaded, 500); // Réessaye après 500ms
            return;
        }
        console.log("✅ Tableau trouvé, chargement des données...");
        loadTableData();
        waitForPaginationElements(); // Attendre que les éléments de pagination soient chargés
    }

    // Fonction loadTableData() d'origine (inchangée, limite aux 10 premières lignes)
    function loadTableData() {
        fetch("http://127.0.0.1:8000/data/")  
            .then(response => response.json())
            .then(data => {
                allData = data;         // Stocke toutes les données
                filteredData = data;    // Par défaut, pas de filtre
                const tableBody = document.querySelector("#data-table tbody");
                tableBody.innerHTML = ""; 
                
                if (allData.length === 0) {
                    tableBody.innerHTML = "<tr><td colspan='11'>Aucune donnée disponible</td></tr>";
                    return;
                }
                
                // Affiche la première page (10 premières lignes)
                displayPage(1);
            })
            .catch(error => console.error("🚨 Erreur lors du chargement des données :", error));
    }

    // Applique les filtres
    function applyFilters() {
        const countryFilter = document.getElementById("country").value;
        const omsFilter = document.getElementById("omsRegion").value;
        const dateFilter = document.getElementById("date").value;

        filteredData = allData.filter(row => {
            let match = true;
            
            // Filtre par pays
            if (countryFilter !== "all") {
                // compare "china" === "china" etc.
                match = match && row.country.toLowerCase() === countryFilter.toLowerCase();
            }

            // Filtre par région OMS
            if (omsFilter !== "all") {
                match = match && row.who_region.toLowerCase() === omsFilter.toLowerCase();
            }

            // Filtre par date
            if (dateFilter) {
                // row.date doit correspondre exactement, ex: "2020-01-23"
                match = match && row.date === dateFilter;
            }

            return match;
        });

        currentPage = 1;       // Réinitialise la page
        displayPage(currentPage);
    }

    // Affiche la page demandée
    function displayPage(page) {
        const tableBody = document.querySelector("#data-table tbody");
        tableBody.innerHTML = ""; // Efface les lignes actuelles

        // On affiche filteredData (si un filtre est actif) ou allData (si pas de filtre)
        // Ici, on a mis filteredData = allData par défaut, donc on utilise toujours filteredData
        const start = (page - 1) * rowsPerPage;
        const end = start + rowsPerPage;
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
                <td>${row.mortality_rate ?? "N/A"}%</td>
                <td>${row.recovery_rate ?? "N/A"}%</td>
            `;
            tableBody.appendChild(tr);
        });

        // Mettre à jour l'affichage de la pagination
        const totalPages = Math.ceil(filteredData.length / rowsPerPage);
        const pageInfo = document.querySelector("#pageInfo");
        if (pageInfo) {
            pageInfo.textContent = `Page ${currentPage} / ${totalPages}`;
        }
        const prevBtn = document.querySelector("#prevPage");
        const nextBtn = document.querySelector("#nextPage");
        if (prevBtn) prevBtn.disabled = currentPage === 1;
        if (nextBtn) nextBtn.disabled = currentPage === totalPages;
    }

    function waitForFilterElements() {
        const countrySelect = document.getElementById("country");
        const omsSelect = document.getElementById("omsRegion");
        const dateInput = document.getElementById("date");
      
        if (!countrySelect || !omsSelect || !dateInput) {
          console.warn("⏳ Éléments de filtre non encore disponibles, nouvelle tentative...");
          setTimeout(waitForFilterElements, 500);
          return;
        }
      
        // Une fois trouvés, on peut attacher les écouteurs
        countrySelect.addEventListener("change", applyFilters);
        omsSelect.addEventListener("change", applyFilters);
        dateInput.addEventListener("change", applyFilters);
      }
      
      // Puis, appelez cette fonction
      waitForFilterElements();      

    // Fonction pour attacher les écouteurs aux boutons de pagination une fois qu'ils sont présents
    function waitForPaginationElements() {
        const prevBtn = document.querySelector("#prevPage");
        const nextBtn = document.querySelector("#nextPage");
        const pageInfo = document.querySelector("#pageInfo");

        if (!prevBtn || !nextBtn || !pageInfo) {
            // Si l'un des éléments n'est pas trouvé, réessayer après 500ms
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

    checkTableLoaded();

    // Écouteurs sur les filtres
    document.getElementById("country").addEventListener("change", applyFilters);
    document.getElementById("omsRegion").addEventListener("change", applyFilters);
    document.getElementById("date").addEventListener("change", applyFilters);

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
