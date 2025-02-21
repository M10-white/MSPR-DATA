document.addEventListener('DOMContentLoaded', () => {
    // Sélectionner les conteneurs où les composants seront injectés
    const dashboardContainer = document.querySelector('#dashboard');

    // Vérifiez que le conteneur existe
    if (!dashboardContainer) {
        console.error('Dashboard container not found');
        return;
    }

    // Fonction pour faire une requête API
    async function fetchData(url) {
        try {
            console.log(`Fetching data from ${url}`);
            const response = await fetch(url, {
                mode: 'cors' // S'assurer que CORS est bien activé
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            console.log(`Données reçues de ${url}:`, data);
            return data;
        } catch (error) {
            console.error(`Erreur lors de la récupération des données depuis ${url}:`, error);
            return null;
        }
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

    // Fonction pour afficher les données dans un graphique
    function displayChartData(data) {
        const canvas = document.getElementById('chart-1');
        if (!canvas) {
            console.error("Chart canvas not found");
            return;
        }

        const ctx = canvas.getContext('2d');
        const chartData = {
            labels: data.map(item => item.date),
            datasets: [
                {
                    label: 'Cas confirmés',
                    data: data.map(item => item.confirmed),
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                },
                {
                    label: 'Morts',
                    data: data.map(item => item.deaths),
                    borderColor: 'rgba(255, 99, 132, 1)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                }
            ],
        };

        new Chart(ctx, {
            type: 'line',
            data: chartData,
            options: {
                responsive: true,
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'day'
                        }
                    }
                }
            }
        });
    }

    // Charger les données et les afficher
    async function loadData() {
        try {
            const covidData = await fetchData('http://127.0.0.1:8000/api/v1/covid-data');
            const countryData = await fetchData('http://127.0.0.1:8000/api/v1/country-data');

            if (countryData) {
                displayTableData(countryData);
            } else {
                console.error("Les données du tableau sont vides.");
            }

            if (covidData) {
                displayChartData(covidData);
            } else {
                console.error("Les données du graphique sont vides.");
            }
        } catch (error) {
            console.error('Error fetching data:', error);
        }
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
