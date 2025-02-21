from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# Détermine le bon chemin vers le dossier public
static_dir = os.path.abspath("../frontend/public")

# Monte le dossier public comme dossier statique
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

# Configuration CORS pour permettre toutes les origines
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permet l'accès depuis n'importe quelle origine
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the COVID-19 API"}

# Route pour récupérer les données COVID
@app.get("/api/v1/covid-data")
def get_covid_data():
    covid_data = [
        {"date": "2025-01-20", "confirmed": 100, "deaths": 5},
        {"date": "2025-01-21", "confirmed": 150, "deaths": 10},
        {"date": "2025-01-22", "confirmed": 235, "deaths": 58},
    ]
    return covid_data

@app.get("/api/v1/country-data")
def get_country_data():
    country_data = [
        {"name": "France", "transmission_rate": 1.2, "mortality": 0.02, "region": "Europe"},
        {"name": "USA", "transmission_rate": 1.5, "mortality": 0.03, "region": "North America"},
    ]
    return country_data
