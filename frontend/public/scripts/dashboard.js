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
        const response = await fetch(url, {
            mode: 'cors'
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    }

    // Fonction pour afficher les données dans un tableau
    function displayTableData(data) {
        const tableBody = document.querySelector('.data-table tbody');
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
        const ctx = document.getElementById('chart-1').getContext('2d');
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
            const covidData = await fetchData('http://localhost:8000/api/v1/covid-data');
            const countryData = await fetchData('http://localhost:8000/api/v1/country-data');

            displayTableData(countryData);
            displayChartData(covidData);
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
            document.querySelector('.charts').innerHTML = chartHtml;

            const tableResp = await fetch('components/table.html');
            const tableHtml = await tableResp.text();
            document.querySelector('.data-table').innerHTML = tableHtml;

            // Charger les données après le chargement des composants
            loadData();
        } catch (error) {
            console.error('Error loading components:', error);
        }
    }

    // Charger les composants au démarrage
    loadComponents();
});