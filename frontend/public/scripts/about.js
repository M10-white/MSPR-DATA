document.addEventListener('DOMContentLoaded', async () => {
    const componentsPandemics = [
        { id: 'header', file: 'components/header.html' }
    ];
    

    for (const { id, file } of componentsPandemics) {
        const response = await fetch(file);
        const html = await response.text();
        document.getElementById(id).innerHTML = html;
    }
});