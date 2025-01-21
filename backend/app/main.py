from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configurez CORS
origins = [
    "http://127.0.0.1:5000",
    "http://localhost:5000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the COVID-19 API"}

# Définissez vos routes API ici
@app.get("/api/v1/covid-data")
def get_covid_data():
    # Exemple de données, remplacez-les par votre logique
    covid_data = [
        {"date": "2025-01-20", "confirmed": 100, "deaths": 5},
        {"date": "2025-01-21", "confirmed": 150, "deaths": 10},
        {"date": "2025-01-22", "confirmed": 235, "deaths": 58},
    ]
    return covid_data

@app.get("/api/v1/country-data")
def get_country_data():
    # Exemple de données, remplacez-les par votre logique
    country_data = [
        {"name": "France", "transmission_rate": 1.2, "mortality": 0.02, "region": "Europe"},
        {"name": "USA", "transmission_rate": 1.5, "mortality": 0.03, "region": "North America"},
    ]
    return country_data