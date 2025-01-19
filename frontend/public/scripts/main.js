function addAnimations() {
    const elementsToAnimate = document.querySelectorAll('#header, #footer, #dashboard, .filter-bar, .chart, .data-table');

    elementsToAnimate.forEach((element, index) => {
        element.classList.add('fade-in');
        element.style.animationDelay = `${index * 0.2}s`;
    });
}

// Ajout d'un appel à cette fonction après le chargement des composants
document.addEventListener('DOMContentLoaded', async () => {
    const components = [
        { id: 'header', file: '../components/header.html' },
        { id: 'dashboard', file: '../components/dashboard.html' }
        // { id: 'footer', file: '../components/footer.html' }
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
        document.querySelector(`.${id}`).innerHTML = html;
    }

    // Faut ajouter d'autres animations ici
    addAnimations();
});
