document.addEventListener('DOMContentLoaded', () => {
    // Sélectionner les conteneurs où les composants seront injectés
    const dashboardContainer = document.querySelector('#dashboard');

    // Vérifiez que le conteneur existe
    if (!dashboardContainer) {
        console.error('Dashboard container not found');
        return;
    }

    // Fonction pour afficher les données dans un tableau
    function displayTableData(data) {
        const tableBody = document.querySelector('.data-table tbody');
        if (!tableBody) {
            console.error("Table body not found");
            return;
        }

        tableBody.innerHTML = ""; // Vider le tableau avant d'ajouter de nouvelles données

        data.forEach(item => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${item.name}</td>
                <td>${item.transmission_rate}</td>
                <td>${item.mortality}</td>
                <td>${item.region}</td>
            `;
            tableBody.appendChild(row);
        });
    }

    // Charger les composants HTML et injecter les données
    async function loadComponents() {
        try {
            const dashboardResp = await fetch('components/dashboard.html');
            const dashboardHtml = await dashboardResp.text();
            dashboardContainer.innerHTML = dashboardHtml;

            // Après avoir injecté le HTML, charger les composants individuels
            const chartResp = await fetch('components/chart.html');
            const chartHtml = await chartResp.text();
            const chartsContainer = document.querySelector('.charts');
            if (chartsContainer) chartsContainer.innerHTML = chartHtml;

            const tableResp = await fetch('components/table.html');
            const tableHtml = await tableResp.text();
            const tableContainer = document.querySelector('.data-table');
            if (tableContainer) tableContainer.innerHTML = tableHtml;

            // Charger les données après le chargement des composants
            loadData();
        } catch (error) {
            console.error('Error loading components:', error);
        }
    }

    // Charger les composants au démarrage
    loadComponents();
});
