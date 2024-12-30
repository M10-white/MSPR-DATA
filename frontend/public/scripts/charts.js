import { fetchData } from './api.js';

async function renderChart() {
    const data = await fetchData('pandemics');
    const ctx = document.getElementById('myChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(d => d.name),
            datasets: [{
                label: 'Taux de transmission',
                data: data.map(d => d.transmissionRate),
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        }
    });
}

renderChart();