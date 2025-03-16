console.log("🔍 Début du chargement de pandemics.js");

// 🔎 Vérification du `localStorage` et des cookies avant exécution
console.log("📦 Contenu actuel de localStorage:", JSON.stringify(localStorage, null, 2));
console.log("🍪 Contenu des cookies:", document.cookie);

document.addEventListener('DOMContentLoaded', async () => {
    console.log("🚀 DOM chargé, initialisation des composants...");

    const componentsPandemics = [
        { id: 'header', file: 'components/header.html' },
        { id: 'dashboard-pandemics', file: 'components/dashboard-pandemics.html' },
    ];

    for (const { id, file } of componentsPandemics) {
        try {
            const response = await fetch(file);
            if (!response.ok) throw new Error(`Erreur HTTP ${response.status}`);

            let html = await response.text();
            
            // ✅ Vérifier si un mauvais <link> styles.css est injecté
            html = html.replace('<link rel="stylesheet" href="styles.css">', `
                <link rel="stylesheet" href="styles/main.css">
                <link rel="stylesheet" href="styles/dashboard.css">
            `);

            const container = document.getElementById(id);
            if (container) {
                container.innerHTML = html;
                console.log(`✅ ${file} chargé dans #${id}`);
            } else {
                console.error(`🚨 Impossible de trouver l'élément #${id} dans le DOM`);
            }
        } catch (error) {
            console.error(`🚨 Erreur lors du chargement du fichier ${file} :`, error);
        }
    }

    async function waitForElement(selector, maxRetries = 20, delay = 500) {
        let retries = 0;
        while (!document.querySelector(selector) && retries < maxRetries) {
            console.warn(`⏳ Attente de ${selector}... Tentative ${retries + 1}/${maxRetries}`);
            await new Promise(resolve => setTimeout(resolve, delay));
            retries++;
        }
        return document.querySelector(selector);
    }

    async function getUserId() {
        let userId = sessionStorage.getItem("user_id") || localStorage.getItem("user_id");

        if (userId) {
            console.log(`✅ user_id récupéré : ${userId}`);
            return Number(userId);
        }

        console.warn("⚠️ user_id non trouvé, vérification des cookies...");
        const cookies = document.cookie.split("; ");
        for (let cookie of cookies) {
            let [name, value] = cookie.split("=");
            if (name.trim() === "user_id") {
                console.log(`✅ user_id récupéré depuis Cookie: ${value}`);
                sessionStorage.setItem("user_id", value);
                localStorage.setItem("user_id", value);
                return Number(value);
            }
        }

        console.error("❌ Aucun user_id trouvé !");
        return null;
    }

    let userId = await getUserId();
    if (!userId) {
        alert("⚠️ Problème de connexion : aucun user_id trouvé !");
        return;
    }
    console.log(`🔹 userId final : ${userId}`);

    let allData = [];
    let filteredData = [];
    let currentPage = 1;
    const rowsPerPage = 10;

    async function loadTableData() {
        try {
            console.log(`📡 Requête API : Récupération des données pour userId: ${userId}`);
            const url = `http://127.0.0.1:5000/data/${userId}`;

            const response = await fetch(url);
            if (!response.ok) throw new Error(`Erreur HTTP ${response.status}`);

            allData = await response.json();
            filteredData = allData; // Par défaut, aucune donnée filtrée

            console.log("📊 Données reçues de l'API :", allData);
            await displayPage(currentPage);
        } catch (error) {
            console.error("🚨 Erreur lors du chargement des données :", error);
        }
    }

    // Appliquer les filtres
    function applyFilters() {
        const countryFilter = document.getElementById("country").value;
        const omsFilter = document.getElementById("omsRegion").value;
        const dateFilter = document.getElementById("date").value;

        filteredData = allData.filter(row => {
            let match = true;

            if (countryFilter !== "all") {
                match = match && row.country.toLowerCase() === countryFilter.toLowerCase();
            }

            if (omsFilter !== "all") {
                match = match && row.who_region.toLowerCase() === omsFilter.toLowerCase();
            }

            if (dateFilter) {
                match = match && row.date === dateFilter;
            }

            return match;
        });

        currentPage = 1; // Réinitialise la page
        displayPage(currentPage);
    }

    // Affiche les données de la page
    function displayPage(page) {
        const tableBody = document.querySelector("#table-body");
        tableBody.innerHTML = "";

        const start = (page - 1) * rowsPerPage;
        const end = start + rowsPerPage;
        const pageData = filteredData.slice(start, end);

        if (pageData.length === 0) {
            tableBody.innerHTML = "<tr><td colspan='12'>Aucune donnée disponible</td></tr>";
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

        const totalPages = Math.ceil(filteredData.length / rowsPerPage);
        const pageInfo = document.querySelector("#pageInfo");
        if (pageInfo) {
            pageInfo.textContent = `Page ${currentPage} / ${totalPages}`;
        }
        const prevBtn = document.querySelector("#prevPage");
        const nextBtn = document.querySelector("#nextPage");

        if (prevBtn) prevBtn.disabled = currentPage === 1;
        if (nextBtn) nextBtn.disabled = currentPage === totalPages;
    }

    // Fonction d'attente des éléments de pagination
    function waitForPaginationElements() {
        const prevBtn = document.querySelector("#prevPage");
        const nextBtn = document.querySelector("#nextPage");

        if (!prevBtn || !nextBtn) {
            setTimeout(waitForPaginationElements, 500);
            return;
        }

        prevBtn.addEventListener("click", () => {
            if (currentPage > 1) {
                currentPage--;
                displayPage(currentPage);
            }
        });

        nextBtn.addEventListener("click", () => {
            if (currentPage < Math.ceil(filteredData.length / rowsPerPage)) {
                currentPage++;
                displayPage(currentPage);
            }
        });
    }

    // Fonction d'attente des éléments de filtre
    function waitForFilterElements() {
        const countrySelect = document.getElementById("country");
        const omsSelect = document.getElementById("omsRegion");
        const dateInput = document.getElementById("date");

        if (!countrySelect || !omsSelect || !dateInput) {
            setTimeout(waitForFilterElements, 500);
            return;
        }

        countrySelect.addEventListener("change", applyFilters);
        omsSelect.addEventListener("change", applyFilters);
        dateInput.addEventListener("change", applyFilters);
    }

    // Écouteurs pour les éléments de pagination et les filtres
    waitForPaginationElements();
    waitForFilterElements();

    // Chargement des données de la table
    checkTableLoaded();

    // 📌 Requête POST : Ajouter une nouvelle entrée
    document.getElementById("addForm").addEventListener("submit", async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        const newEntry = Object.fromEntries(formData.entries());
        newEntry.user_id = userId;

        try {
            const response = await fetch("http://127.0.0.1:5000/data/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(newEntry),
            });

            if (!response.ok) throw new Error(await response.text());

            alert("✅ Donnée ajoutée !");
            loadTableData();
            e.target.reset();
        } catch (err) {
            console.error("🚨 Erreur POST :", err);
            alert("⚠️ Échec de l'ajout !");
        }
    });

    // 📌 Requêtes DELETE et PUT (modification/suppression)
    document.addEventListener("click", async (event) => {  // Ajout de `async` ici
        console.log("🖱️ Click détecté sur :", event.target);

        // 📌 Requête Modifier
        if (event.target.classList.contains("btn-modifier")) {
            console.log("✅ Bouton Modifier cliqué !");
            const rowId = event.target.dataset.id;
            const row = allData.find(item => item.id == rowId);

            if (row) {
                console.log(`🔄 Modification en cours pour l'ID ${rowId}`);

                // Sélection de la pop-up et du formulaire
                const modal = document.getElementById("updateModal");
                const form = document.getElementById("updateFormModal");

                if (!modal || !form) {
                    console.error("❌ Pop-up ou formulaire introuvable !");
                    return;
                }

                const userId = sessionStorage.getItem("user_id") || localStorage.getItem("user_id");
                if (!userId) {
                    alert("⚠️ Erreur : aucun user_id trouvé !");
                    return;
                }

                // Remplissage des champs avec les données existantes
                form.elements["id"].value = row.id;
                form.elements["country"].value = row.country;
                form.elements["date"].value = row.date;
                form.elements["cases"].value = row.cases;
                form.elements["deaths"].value = row.deaths;
                form.elements["recovered"].value = row.recovered;
                form.elements["active"].value = row.active;
                form.elements["latitude"].value = row.latitude ?? "";
                form.elements["longitude"].value = row.longitude ?? "";
                form.elements["who_region"].value = row.who_region ?? "";
                form.elements["mortality_rate"].value = row.mortality_rate ?? "";
                form.elements["recovery_rate"].value = row.recovery_rate ?? "";

                // Affichage de la pop-up
                console.log("📌 Ouverture de la pop-up de modification...");
                modal.style.display = "flex"; // Assurer l'affichage
                modal.classList.remove("hidden");
                setTimeout(() => {
                    modal.classList.add("active");
                }, 10);

                // Gestion de la soumission du formulaire
                form.onsubmit = async (e) => {
                    e.preventDefault();

                    const updatedData = {
                        cases: form.elements["cases"].value,
                        deaths: form.elements["deaths"].value,
                        recovered: form.elements["recovered"].value,
                        active: form.elements["active"].value,
                        latitude: form.elements["latitude"].value || null,
                        longitude: form.elements["longitude"].value || null,
                        who_region: form.elements["who_region"].value || null,
                        mortality_rate: form.elements["mortality_rate"].value || null,
                        recovery_rate: form.elements["recovery_rate"].value || null
                    };

                    try {
                        const apiUrl = `http://127.0.0.1:5000/data/${userId}/${row.country}/${row.date}`;
                        console.log(`🔄 Envoi de la requête PUT à : ${apiUrl}`);

                        const response = await fetch(apiUrl, {
                            method: "PUT",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify(updatedData),
                        });

                        if (!response.ok) throw new Error(await response.text());

                        alert("✅ Donnée mise à jour !");
                        modal.classList.remove("active");
                        setTimeout(() => {
                            modal.classList.add("hidden");
                            modal.style.display = "none";
                        }, 300);

                        loadTableData(); 
                    } catch (err) {
                        console.error("🚨 Erreur lors de la mise à jour :", err);
                        alert("⚠️ Échec de la modification !");
                    }
                };

                // Gestion du bouton "Annuler"
                document.getElementById("cancelUpdate").addEventListener("click", () => {
                    console.log("❌ Annulation de la modification");
                    modal.classList.remove("active");
                    setTimeout(() => {
                        modal.classList.add("hidden");
                        modal.style.display = "none";
                    }, 300);
                });
            }
        }

        // 🗑️ Suppression d'une donnée
        if (event.target.classList.contains("btn-supprimer")) {
            console.log("✅ Bouton Supprimer cliqué !");
            const rowId = event.target.dataset.id;
            const row = allData.find(item => item.id == rowId);

            if (row) {
                console.log(`🔄 Suppression en cours pour l'ID ${rowId}`);

                const userId = sessionStorage.getItem("user_id") || localStorage.getItem("user_id");
                if (!userId) {
                    alert("⚠️ Erreur : aucun user_id trouvé !");
                    return;
                }

                const confirmation = confirm(`Êtes-vous sûr de vouloir supprimer la donnée pour ${row.country} ?`);

                if (confirmation) {
                    try {
                        // Correction de l'URL pour la suppression : on utilise uniquement l'ID
                        const apiUrl = `http://127.0.0.1:5000/data/${row.id}`;
                        console.log(`🔄 Envoi de la requête DELETE à : ${apiUrl}`);

                        const response = await fetch(apiUrl, {
                            method: "DELETE",
                        });

                        if (!response.ok) throw new Error(await response.text());

                        alert("✅ Donnée supprimée !");
                        loadTableData(); 
                    } catch (err) {
                        console.error("🚨 Erreur lors de la suppression :", err);
                        alert("⚠️ Échec de la suppression !");
                    }
                }
            }
        }
    });

    await waitForElement("#dashboard-pandemics");
    await waitForElement("#dashboard-pandemics table");
    await waitForElement("#table-body");
    console.log("📌 Composants bien chargés, lancement de loadTableData()");
    await loadTableData();
});
