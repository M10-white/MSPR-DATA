from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import pandas as pd
from typing import Optional
from pydantic import BaseModel, EmailStr

class UserLogin(BaseModel):
    email: EmailStr
    password: str

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
    user_id: int  # Ajout de la relation avec l'utilisateur
    country: str
    date: str
    cases: int
    deaths: int
    recovered: int
    active: int
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    who_region: Optional[str] = None
    mortality_rate: Optional[float] = None
    recovery_rate: Optional[float] = None

class User(BaseModel):
    username: str
    email: str
    password: str

# 💌 CRUD pour Users
@app.get("/users/")
def get_all_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, password, created_at FROM users")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    users = []
    for r in rows:
        users.append({
            "id": r[0],
            "username": r[1],
            "email": r[2],
            "password": r[3],
            "created_at": r[4]
        })
    return users

@app.post("/users/")
def create_user(user: User):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO users (username, email, password) 
        VALUES (%s, %s, %s) RETURNING id;
    """, (user.username, user.email, user.password))
    
    user_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "✅ Utilisateur créé avec succès", "user_id": user_id}

@app.get("/users/{user_id}")
def get_user(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return {"id": user[0], "username": user[1], "email": user[2]}

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "✅ Utilisateur supprimé avec succès"}

@app.put("/users/{user_id}")
def update_user(user_id: int, updated_user: User):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Vérifie que l'utilisateur existe
    cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
    if cursor.fetchone() is None:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Met à jour l'utilisateur
    cursor.execute("""
        UPDATE users
        SET username = %s,
            email = %s,
            password = %s
        WHERE id = %s
    """, (updated_user.username, updated_user.email, updated_user.password, user_id))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "✅ Utilisateur mis à jour avec succès"}


# 💌 CRUD pour PandemicData
@app.get("/data/")
def get_data(user_id: Optional[int] = Query(None), country: Optional[str] = Query(None), start_date: Optional[str] = Query(None), end_date: Optional[str] = Query(None)):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT user_id, country, date, cases, deaths, recovered, active, latitude, longitude, who_region, mortality_rate, recovery_rate 
        FROM pandemic_data WHERE 1=1
    """
    params = []

    if user_id:
        query += " AND user_id = %s"
        params.append(user_id)

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

    columns = ["user_id", "country", "date", "cases", "deaths", "recovered", "active", "latitude", "longitude", "who_region", "mortality_rate", "recovery_rate"]
    df = pd.DataFrame(data, columns=columns)

    cursor.close()
    conn.close()

    return df.to_dict(orient="records")

@app.post("/data/")
def add_data(entry: PandemicData):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO pandemic_data (user_id, country, date, cases, deaths, recovered, active, latitude, longitude, who_region, mortality_rate, recovery_rate)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (entry.user_id, entry.country, entry.date, entry.cases, entry.deaths, entry.recovered, entry.active, entry.latitude, entry.longitude, entry.who_region, entry.mortality_rate, entry.recovery_rate))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "✅ Données insérées avec succès"}

@app.delete("/data/")
def delete_data(user_id: int, country: str, date: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pandemic_data WHERE user_id = %s AND country = %s AND date = %s", (user_id, country, date))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Aucune donnée trouvée pour suppression")
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "✅ Données supprimées avec succès"}

@app.get("/test_connection/")
def test_connection():
    try:
        conn = get_db_connection()
        conn.close()
        return {"status": "✅ Connexion réussie à PostgreSQL"}
    except Exception as e:
        return {"status": "❌ Échec de connexion", "error": str(e)}

@app.post("/login")
def login(user: UserLogin):
    """
    Vérifie si l'email et le mot de passe correspondent à un user en base.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Récupérer l'utilisateur via son email
    cursor.execute("SELECT id, username, email, password FROM users WHERE email = %s", (user.email,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row:
        # Aucun user avec cet email
        raise HTTPException(status_code=400, detail="Email ou mot de passe incorrect")
    
    user_id, username, email, db_password = row

    # Vérification du mot de passe (exemple simplifié, sans hachage)
    if user.password != db_password:
        raise HTTPException(status_code=400, detail="Email ou mot de passe incorrect")

    # Si OK, on renvoie un message de succès ou un token
    return {
        "message": "Connexion réussie !",
        "user_id": user_id,
        "username": username
    }

# 💌 Lancer l'API avec uvicorn
# Commande : uvicorn fastapi_postgres_api:app --reload
