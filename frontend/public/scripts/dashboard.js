document.addEventListener("DOMContentLoaded", function () {
    console.log("🚀 Script chargé, recherche du tableau...");

    function checkTableLoaded() {
        const tableBody = document.querySelector("#data-table");

        if (!tableBody) {
            console.warn("⏳ Tableau non encore disponible, nouvelle tentative...");
            setTimeout(checkTableLoaded, 500); // Réessaye après 500ms
            return;
        }

        console.log("✅ Tableau trouvé, chargement des données...");
        loadTableData();
    }

    function loadTableData() {
        fetch("http://127.0.0.1:8000/data/")  
            .then(response => response.json())
            .then(data => {
                const tableBody = document.querySelector("#data-table tbody");
                tableBody.innerHTML = ""; 
                
                if (data.length === 0) {
                    tableBody.innerHTML = "<tr><td colspan='11'>Aucune donnée disponible</td></tr>";
                    return;
                }

                data.forEach(row => {
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
            })
            .catch(error => console.error("🚨 Erreur lors du chargement des données :", error));
    }

    checkTableLoaded();
});
