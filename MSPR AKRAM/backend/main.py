# backend/main.py

# Importe la classe FastAPI pour créer l'application web.
from fastapi import FastAPI
# Importe le module `database` qui contient la logique d'initialisation de la base de données.
import database
# Importe le module 'models' pour s'assurer que les modèles de base de données sont reconnus par SQLAlchemy avant l'initialisation de la base de données.
import models
# Importe les routeurs définis dans `routes.py` pour les endpoints de l'API (données, prédiction).
from routes import router as api_router
# Importe le routeur d'authentification défini dans `auth.py`.
from auth import router as auth_router

# Crée une instance de l'application FastAPI avec un titre descriptif.
app = FastAPI(title="MSPR API IA Pandémies")

# Définit un événement de démarrage qui sera exécuté au lancement de l'application.
@app.on_event("startup")
def on_startup():
    # Initialise la base de données lorsque l'application démarre.
    # Cela inclut généralement la création des tables si elles n'existent pas.
    database.init_db()

# Inclut le routeur des API générales sous le préfixe '/api'.
# Toutes les routes définies dans `routes.py` seront accessibles via /api/your-endpoint.
app.include_router(api_router, prefix="/api")
# Inclut le routeur d'authentification sous le même préfixe '/api'.
# Les routes d'authentification (ex: /api/login, /api/register) seront accessibles.
app.include_router(auth_router, prefix="/api") 