document.addEventListener('DOMContentLoaded', async () => {
    const components = [
        { id: 'header', file: '../components/header.html' },
        { id: 'dashboard', file: '../components/dashboard.html' }
    ];

    for (const { id, file } of components) {
        const response = await fetch(file);
        const html = await response.text();
        document.getElementById(id).innerHTML = html;
    }

    // Charge les sous-composants du Dashboard
    const dashboardComponents = [
        { id: 'filter-bar', file: '../components/filter-bar.html' },
        { id: 'charts', file: '../components/chart.html' },
        { id: 'data-table', file: '../components/table.html' }
    ];

    for (const { id, file } of dashboardComponents) {
        const response = await fetch(file);
        const html = await response.text();
        const container = document.querySelector(`.${id}`);

        if (container) {
            container.innerHTML = html;
        } else {
            console.error(`🚨 Impossible de trouver l'élément .${id} dans le DOM`);
        }
    }

    console.log("✅ Tous les composants sont chargés, lancement de dashboard.js...");
    const script = document.createElement("script");
    script.src = "scripts/dashboard.js";
    script.defer = true;
    document.body.appendChild(script);

    addAnimations();
});
