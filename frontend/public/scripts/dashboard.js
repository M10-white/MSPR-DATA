document.addEventListener("DOMContentLoaded", function () {
    console.log("🚀 Script chargé, recherche du tableau...");

    // Variables pour la pagination
    let allData = [];         // Stocke toutes les données récupérées
    let currentPage = 1;
    let filteredData = [];
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
                allData = data; // Stocke toutes les données
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

    // Fonction pour afficher la page demandée
    function displayPage(page) {
        const tableBody = document.querySelector("#data-table tbody");
        tableBody.innerHTML = ""; // Efface les lignes actuelles

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
            tableBody.appendChild(tr);
        });

        // Mettre à jour l'affichage de la pagination
        const totalPages = Math.ceil(allData.length / rowsPerPage);
        const pageInfo = document.querySelector("#pageInfo");
        if (pageInfo) {
            pageInfo.textContent = `Page ${currentPage} / ${totalPages}`;
        }
        const prevBtn = document.querySelector("#prevPage");
        const nextBtn = document.querySelector("#nextPage");
        if (prevBtn) prevBtn.disabled = currentPage === 1;
        if (nextBtn) nextBtn.disabled = currentPage === totalPages;
    }

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

        // Ajouter les écouteurs d'événements si ce n'est pas déjà fait
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
    
    loadTableData();
    checkTableLoaded();
});
