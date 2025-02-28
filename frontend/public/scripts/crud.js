document.addEventListener("DOMContentLoaded", function () {
  // Fonctions pour afficher/cacher la pop-up
  function showPopup(message, callback) {
    const popup = document.getElementById('popup');
    const popupMessage = document.getElementById('popupMessage');
    popupMessage.textContent = message;
    popup.classList.remove('hidden');

    const closeButton = document.getElementById('popupClose');
    closeButton.onclick = function() {
      hidePopup();
      if (callback) callback();
    };
  }
  
  function hidePopup() {
    const popup = document.getElementById('popup');
    popup.classList.add('hidden');
  }
  
  // Fonction qui attend que les formulaires CRUD soient chargés dans le DOM
  function waitForCrudForms() {
    const addForm = document.getElementById("addForm");
    const updateForm = document.getElementById("updateForm");
    const deleteForm = document.getElementById("deleteForm");

    if (!addForm || !updateForm || !deleteForm) {
      console.warn("Les formulaires CRUD ne sont pas encore disponibles, nouvelle tentative...");
      setTimeout(waitForCrudForms, 500);
      return;
    }

    // Ajout d'une donnée (POST)
    addForm.addEventListener("submit", function(e) {
      e.preventDefault();
      const formData = new FormData(this);
      const data = Object.fromEntries(formData.entries());
      data.cases = parseInt(data.cases);
      data.deaths = parseInt(data.deaths);
      data.recovered = parseInt(data.recovered);
      data.active = parseInt(data.active);
      if (data.latitude) data.latitude = parseFloat(data.latitude);
      if (data.longitude) data.longitude = parseFloat(data.longitude);
      if (data.mortality_rate) data.mortality_rate = parseFloat(data.mortality_rate);
      if (data.recovery_rate) data.recovery_rate = parseFloat(data.recovery_rate);
    
      fetch("http://127.0.0.1:8000/data/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
      })
      .then(res => res.json())
      .then(result => {
        showPopup("Donnée ajoutée avec succès !", function() {
          location.reload();
        });
      })
      .catch(err => {
        console.error("Erreur lors de l'ajout :", err);
        showPopup("Erreur lors de l'ajout de la donnée !");
      });
    });

    // Modification d'une donnée (PUT)
    updateForm.addEventListener("submit", function(e) {
      e.preventDefault();
      const formData = new FormData(this);
      const data = Object.fromEntries(formData.entries());
      data.cases = parseInt(data.cases);
      data.deaths = parseInt(data.deaths);
      data.recovered = parseInt(data.recovered);
      data.active = parseInt(data.active);
      if (data.latitude) data.latitude = parseFloat(data.latitude);
      if (data.longitude) data.longitude = parseFloat(data.longitude);
      if (data.mortality_rate) data.mortality_rate = parseFloat(data.mortality_rate);
      if (data.recovery_rate) data.recovery_rate = parseFloat(data.recovery_rate);
    
      fetch("http://127.0.0.1:8000/data/update/", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
      })
      .then(res => res.json())
      .then(result => {
        showPopup("Donnée modifiée avec succès !", function() {
          location.reload();
        });
      })
      .catch(err => {
        console.error("Erreur lors de la modification :", err);
        showPopup("Erreur lors de la modification de la donnée !");
      });
    });

    // Suppression d'une donnée (DELETE)
    deleteForm.addEventListener("submit", function(e) {
      e.preventDefault();
      const formData = new FormData(this);
      const params = new URLSearchParams(Object.fromEntries(formData.entries()));
    
      fetch("http://127.0.0.1:8000/data/?" + params.toString(), {
        method: "DELETE"
      })
      .then(res => res.json())
      .then(result => {
        showPopup("Donnée supprimée avec succès !", function() {
          location.reload();
        });
      })
      .catch(err => {
        console.error("Erreur lors de la suppression :", err);
        showPopup("Erreur lors de la suppression de la donnée !");
      });
    });

    console.log("✅ Formulaires CRUD chargés et écouteurs attachés.");
  }

  waitForCrudForms();
});
