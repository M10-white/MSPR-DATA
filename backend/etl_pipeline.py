from prefect import flow, task
import pandas as pd
import os
import psycopg2
import kaggle
import zipfile
import time

# 📌 Dossier de stockage
DATA_FOLDER = "data"
CSV_FILE = "covid_19_clean_complete.csv"

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

# 📌 Téléchargement des données Kaggle
@task
def download_data():
    os.makedirs(DATA_FOLDER, exist_ok=True)
    dataset_name = "imdevskp/corona-virus-report"
    kaggle.api.dataset_download_files(dataset_name, path=DATA_FOLDER, unzip=True)
    print(f"✅ Données téléchargées et extraites dans {DATA_FOLDER}")

# 📌 Nettoyage et transformation des données
@task
def clean_data():
    file_path = os.path.join(DATA_FOLDER, CSV_FILE)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"❌ Le fichier {CSV_FILE} est introuvable.")
    
    print(f"📂 Chargement et nettoyage du fichier {CSV_FILE}...")
    df = pd.read_csv(file_path, encoding="utf-8", delimiter=",", on_bad_lines="skip")
    
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
    df["active"] = pd.to_numeric(df["active"], errors='coerce').fillna(0).astype(int)
    
    # Correction de 'recovered' si négatif et recalcul de 'active'
    df.loc[df["recovered"] < 0, "recovered"] = df["cases"] - df["deaths"]
    df["active"] = df["cases"] - df["deaths"] - df["recovered"]
    
    # Correction des valeurs négatives de 'active'
    df["active"] = df["active"].apply(lambda x: max(0, x))
    
    # Suppression des valeurs aberrantes
    df = df.dropna(subset=["date"])
    df = df[df["cases"] >= 0]
    df = df[df["deaths"] >= 0]
    df = df[df["recovered"] >= 0]
    df = df[df["active"] >= 0]
    
    # Ajout de nouvelles colonnes dérivées
    df["mortality_rate"] = (df["deaths"] / df["cases"]).fillna(0).apply(lambda x: min(100, x * 100))  # Taux de mortalité limité à 100%
    df["recovery_rate"] = (df["recovered"] / df["cases"]).fillna(0).apply(lambda x: min(100, x * 100))  # Taux de récupération limité à 100%
    
    # Suppression des lignes avec 0 cas pour éviter du bruit
    df = df[df["cases"] > 0]
    
    cleaned_file = os.path.join(DATA_FOLDER, "covid_cleaned.csv")
    df[["country", "latitude", "longitude", "date", "cases", "deaths", "recovered", "active", "who_region", "mortality_rate", "recovery_rate"]].to_csv(cleaned_file, index=False)
    print(f"✅ Données nettoyées et sauvegardées dans {cleaned_file}")
    return cleaned_file


# 📌 Chargement dans PostgreSQL
@task
def load_to_postgres(cleaned_file):
    if not check_postgres():
        raise ConnectionError("Échec de connexion à PostgreSQL.")
    
    conn = psycopg2.connect(
        dbname="pandemics",
        user="postgres",
        password="admin",
        host="localhost",
        port=5432
    )
    cursor = conn.cursor()
    
    # Vérifier et ajouter les colonnes manquantes si besoin
    cursor.execute("""
        ALTER TABLE pandemic_data ADD COLUMN IF NOT EXISTS mortality_rate FLOAT;
        ALTER TABLE pandemic_data ADD COLUMN IF NOT EXISTS recovery_rate FLOAT;
    """)
    
    df = pd.read_csv(cleaned_file)
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO pandemic_data (country, latitude, longitude, date, cases, deaths, recovered, active, who_region, mortality_rate, recovery_rate) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (country, date) 
            DO UPDATE SET 
                cases = EXCLUDED.cases,
                deaths = EXCLUDED.deaths,
                recovered = EXCLUDED.recovered,
                active = EXCLUDED.active,
                who_region = EXCLUDED.who_region,
                mortality_rate = EXCLUDED.mortality_rate,
                recovery_rate = EXCLUDED.recovery_rate;
        """, (row["country"], row["latitude"], row["longitude"], row["date"], row["cases"], row["deaths"], row["recovered"], row["active"], row["who_region"], row["mortality_rate"], row["recovery_rate"]))
    
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Données chargées dans PostgreSQL")

# 📌 Définition du flow Prefect
@flow
def etl_pipeline():
    cleaned_file = clean_data()
    load_to_postgres(cleaned_file)

# 📌 Exécuter le pipeline
if __name__ == "__main__":
    etl_pipeline()
