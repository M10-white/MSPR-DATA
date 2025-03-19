from prefect import flow, task
import pandas as pd
import os
import psycopg2
import time

# 📌 Dossier de stockage
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Récupère le chemin absolu du script
DATA_FOLDER = os.path.join(BASE_DIR, "data")
CSV_FILE = os.path.join(DATA_FOLDER, "covid_19_clean_complete.csv")

# 📌 Vérifier et créer le dossier si nécessaire
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

# 📌 Connexion PostgreSQL
def check_postgres():
    print("🔍 Vérification de la connexion à PostgreSQL...")
    for _ in range(5):
        try:
            conn = psycopg2.connect(
                dbname="pandemics",
                user="postgres",
                password="admin",
                host="localhost",
                port=5432
            )
            conn.close()
            print("✅ Connexion PostgreSQL réussie !")
            return True
        except psycopg2.OperationalError:
            print("⚠️ PostgreSQL inaccessible, nouvelle tentative dans 5s...")
            time.sleep(5)
    print("❌ PostgreSQL inaccessible après plusieurs tentatives.")
    return False

# 📌 Création des tables si elles n'existent pas
def create_tables():
    conn = psycopg2.connect(
        dbname="pandemics",
        user="postgres",
        password="admin",
        host="localhost",
        port=5432
    )
    cursor = conn.cursor()
    
    # 📌 Création de la table users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 📌 Création de la table pandemic_data avec une clé étrangère vers users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pandemic_data (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
            country TEXT NOT NULL,
            latitude FLOAT,
            longitude FLOAT,
            date DATE NOT NULL,
            cases INT,
            deaths INT,
            recovered INT,
            active INT,
            who_region TEXT,
            mortality_rate FLOAT,
            recovery_rate FLOAT,
            UNIQUE (country, date, user_id)
        );
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Tables 'users' et 'pandemic_data' vérifiées/créées avec succès.")

# 📌 Vérification ou création d'un utilisateur par défaut
def get_or_create_user():
    conn = psycopg2.connect(
        dbname="pandemics",
        user="postgres",
        password="admin",
        host="localhost",
        port=5432
    )
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users LIMIT 1;")
    user = cursor.fetchone()

    if not user:
        print("⚠️ Aucun utilisateur trouvé, création d'un utilisateur par défaut...")
        cursor.execute("""
            INSERT INTO users (username, email, password, created_at)
            VALUES ('default_user', 'default@email.com', 'hashed_password', NOW())
            RETURNING id;
        """)
        user_id = cursor.fetchone()[0]
        conn.commit()
    else:
        user_id = user[0]

    cursor.close()
    conn.close()
    return user_id

# 📌 Nettoyage et transformation des données
@task
def clean_data():
    if not os.path.exists(CSV_FILE):
        raise FileNotFoundError(f"❌ Le fichier {CSV_FILE} est introuvable.")
    
    print(f"📂 Chargement et nettoyage du fichier {CSV_FILE}...")
    df = pd.read_csv(CSV_FILE, encoding="utf-8", delimiter=",", on_bad_lines="skip")
    
    df = df.rename(columns={
        "Country/Region": "country",
        "Lat": "latitude",
        "Long": "longitude",
        "Date": "date",
        "Confirmed": "cases",
        "Deaths": "deaths",
        "Recovered": "recovered",
        "Active": "active",
        "WHO Region": "who_region"
    })
    
    df["date"] = pd.to_datetime(df["date"], errors='coerce')
    df["cases"] = pd.to_numeric(df["cases"], errors='coerce').fillna(0).astype(int)
    df["deaths"] = pd.to_numeric(df["deaths"], errors='coerce').fillna(0).astype(int)
    df["recovered"] = pd.to_numeric(df["recovered"], errors='coerce').fillna(0).astype(int)

    df["recovered"] = df.apply(lambda row: min(row["recovered"], row["cases"] - row["deaths"]), axis=1)
    df["active"] = df["cases"] - df["deaths"] - df["recovered"]
    df["active"] = df["active"].apply(lambda x: max(0, x))
    df["mortality_rate"] = (df["deaths"] / df["cases"]).fillna(0).apply(lambda x: min(100, x * 100))  
    df["recovery_rate"] = (df["recovered"] / df["cases"]).fillna(0).apply(lambda x: min(100, x * 100))  
    
    df = df[df["cases"] > 0]
    
    cleaned_file = os.path.join(DATA_FOLDER, "covid_cleaned.csv")
    df.to_csv(cleaned_file, index=False)
    
    print(f"✅ Données nettoyées et sauvegardées dans {cleaned_file}")
    return cleaned_file

# 📌 Chargement dans PostgreSQL
@task
def load_to_postgres(cleaned_file):
    if not check_postgres():
        raise ConnectionError("Échec de connexion à PostgreSQL.")
    
    create_tables()
    user_id = get_or_create_user()
    
    conn = psycopg2.connect(
        dbname="pandemics",
        user="postgres",
        password="admin",
        host="localhost",
        port=5432
    )
    cursor = conn.cursor()
    
    df = pd.read_csv(cleaned_file)
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO pandemic_data (user_id, country, latitude, longitude, date, cases, deaths, recovered, active, who_region, mortality_rate, recovery_rate) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (country, date, user_id) 
            DO UPDATE SET 
                cases = EXCLUDED.cases,
                deaths = EXCLUDED.deaths,
                recovered = EXCLUDED.recovered,
                active = EXCLUDED.active,
                who_region = EXCLUDED.who_region,
                mortality_rate = EXCLUDED.mortality_rate,
                recovery_rate = EXCLUDED.recovery_rate;
        """, (user_id, row["country"], row["latitude"], row["longitude"], row["date"], row["cases"], row["deaths"], row["recovered"], row["active"], row["who_region"], row["mortality_rate"], row["recovery_rate"]))
    
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Données chargées dans PostgreSQL")

@flow
def etl_pipeline():
    cleaned_file = clean_data()
    load_to_postgres(cleaned_file)

if __name__ == "__main__":
    etl_pipeline()