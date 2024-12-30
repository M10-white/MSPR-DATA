const components = ['header', 'footer', 'dashboard', 'filter-bar', 'chart', 'table'];

components.forEach(async (component) => {
    const response = await fetch(`components/${component}.html`);
    const html = await response.text();
    document.querySelector(`#${component}`)?.insertAdjacentHTML('beforeend', html);
});
