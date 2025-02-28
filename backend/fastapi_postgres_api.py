from fastapi import FastAPI, Query, HTTPException, Depends
import psycopg2
import pandas as pd
from typing import Optional
from pydantic import BaseModel

app = FastAPI()

# 📌 Connexion à la base de données PostgreSQL
DATABASE_URL = "dbname=pandemics user=postgres password=admin host=localhost port=5432"

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

# 📌 Modèle Pydantic pour la validation des entrées
class PandemicData(BaseModel):
    country: str
    date: str
    cases: int
    deaths: int
    recovered: int
    active: int
    mortality_rate: Optional[float] = None
    recovery_rate: Optional[float] = None

# 📌 Route pour récupérer des données depuis PostgreSQL
@app.get("/data/")
def get_data(country: Optional[str] = Query(None), start_date: Optional[str] = Query(None), end_date: Optional[str] = Query(None)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT country, date, cases, deaths, recovered, active, mortality_rate, recovery_rate FROM pandemic_data WHERE 1=1"
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
    
    columns = ["country", "date", "cases", "deaths", "recovered", "active", "mortality_rate", "recovery_rate"]
    df = pd.DataFrame(data, columns=columns)
    
    cursor.close()
    conn.close()
    
    return df.to_dict(orient="records")

# 📌 Ajouter une nouvelle entrée dans la BDD
@app.post("/data/")
def add_data(entry: PandemicData):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO pandemic_data (country, date, cases, deaths, recovered, active, mortality_rate, recovery_rate)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (country, date) 
        DO UPDATE SET 
            cases = EXCLUDED.cases,
            deaths = EXCLUDED.deaths,
            recovered = EXCLUDED.recovered,
            active = EXCLUDED.active,
            mortality_rate = EXCLUDED.mortality_rate,
            recovery_rate = EXCLUDED.recovery_rate;
    """, (entry.country, entry.date, entry.cases, entry.deaths, entry.recovered, entry.active, entry.mortality_rate, entry.recovery_rate))
    
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "✅ Données insérées avec succès"}

# 📌 Mettre à jour une entrée existante
@app.put("/data/")
def update_data(entry: PandemicData):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE pandemic_data
        SET cases = %s, deaths = %s, recovered = %s, active = %s, mortality_rate = %s, recovery_rate = %s
        WHERE country = %s AND date = %s
    """, (entry.cases, entry.deaths, entry.recovered, entry.active, entry.mortality_rate, entry.recovery_rate, entry.country, entry.date))
    
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Aucune donnée trouvée pour mise à jour")
    
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "✅ Données mises à jour avec succès"}

# 📌 Supprimer une entrée
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

# 📌 Test de connexion
@app.get("/test_connection/")
def test_connection():
    try:
        conn = get_db_connection()
        conn.close()
        return {"status": "✅ Connexion réussie à PostgreSQL"}
    except Exception as e:
        return {"status": "❌ Échec de connexion", "error": str(e)}

# 📌 Lancer l'API avec uvicorn
# Commande : uvicorn fastapi_postgres_api:app --reload
