from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import pandas as pd
from typing import Optional
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 💌 Connexion à la base de données PostgreSQL
DATABASE_URL = "dbname=pandemics user=postgres password=admin host=localhost port=5432"

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

# 💌 Modèle Pydantic pour la validation des entrées
class PandemicData(BaseModel):
    country: str
    date: str
    cases: int
    deaths: int
    recovered: int
    active: int
    latitude: Optional[float] = None  # Ajout de la latitude
    longitude: Optional[float] = None  # Ajout de la longitude
    who_region: Optional[str] = None  # Ajout de la région OMS
    mortality_rate: Optional[float] = None
    recovery_rate: Optional[float] = None

# 💌 Route pour récupérer des données depuis PostgreSQL
@app.get("/data/")
def get_data(country: Optional[str] = Query(None), start_date: Optional[str] = Query(None), end_date: Optional[str] = Query(None)):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT country, date, cases, deaths, recovered, active, latitude, longitude, who_region, mortality_rate, recovery_rate 
        FROM pandemic_data WHERE 1=1
    """
    params = []

    if country:
        query += " AND country = %s"
        params.append(country)

    if start_date:
        query += " AND date >= %s"
        params.append(start_date)

    if end_date:
        query += " AND date <= %s"
        params.append(end_date)

    cursor.execute(query, tuple(params))
    data = cursor.fetchall()

    columns = ["country", "date", "cases", "deaths", "recovered", "active", "latitude", "longitude", "who_region", "mortality_rate", "recovery_rate"]
    df = pd.DataFrame(data, columns=columns)

    cursor.close()
    conn.close()

    return df.to_dict(orient="records")

# 💌 Ajouter une nouvelle entrée dans la BDD
@app.post("/data/")
def add_data(entry: PandemicData):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO pandemic_data (country, date, cases, deaths, recovered, active, latitude, longitude, who_region, mortality_rate, recovery_rate)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (country, date) 
        DO UPDATE SET 
            cases = EXCLUDED.cases,
            deaths = EXCLUDED.deaths,
            recovered = EXCLUDED.recovered,
            active = EXCLUDED.active,
            latitude = EXCLUDED.latitude,
            longitude = EXCLUDED.longitude,
            who_region = EXCLUDED.who_region,
            mortality_rate = EXCLUDED.mortality_rate,
            recovery_rate = EXCLUDED.recovery_rate;
    """, (entry.country, entry.date, entry.cases, entry.deaths, entry.recovered, entry.active, entry.latitude, entry.longitude, entry.who_region, entry.mortality_rate, entry.recovery_rate))

    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "✅ Données insérées avec succès"}

# 💌 Supprimer une entrée
@app.delete("/data/")
def delete_data(country: str, date: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM pandemic_data WHERE country = %s AND date = %s", (country, date))

    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Aucune donnée trouvée pour suppression")

    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "✅ Données supprimées avec succès"}

# 💌 Test de connexion
@app.get("/test_connection/")
def test_connection():
    try:
        conn = get_db_connection()
        conn.close()
        return {"status": "✅ Connexion réussie à PostgreSQL"}
    except Exception as e:
        return {"status": "❌ Échec de connexion", "error": str(e)}

# 💌 Lancer l'API avec uvicorn
# Commande : uvicorn fastapi_postgres_api:app --reload