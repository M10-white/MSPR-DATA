from prefect import flow, task
import pandas as pd
import os
import psycopg2
import time

# 📌 Dossier contenant les fichiers CSV
DATA_FOLDER = "data"

# 📌 Liste des fichiers CSV à charger
DATASETS = {
    "covid": "WHO_COVID_DATA.csv",  # Nouveau fichier de l'OMS
    "mpox": "owid-monkeypox-data.csv"
}

# 📌 Colonnes standardisées pour uniformiser les données
STANDARD_COLUMNS = ["country", "date", "cases", "deaths"]

# 📌 Vérification PostgreSQL
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

# 📌 Étape 1 : Nettoyer et Uniformiser les Données
@task
def clean_data():
    os.makedirs(DATA_FOLDER, exist_ok=True)
    cleaned_files = {}

    for dataset, filename in DATASETS.items():
        file_path = os.path.join(DATA_FOLDER, filename)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"❌ Le fichier {filename} est introuvable.")

        print(f"📂 Chargement et nettoyage du fichier {filename}...")

        try:
            df = pd.read_csv(file_path, encoding="utf-8", delimiter=",", on_bad_lines="skip")  # ✅ Correction ici
        except Exception as e:
            print(f"⚠️ Erreur de lecture du fichier {filename}: {e}")
            continue

        # 🌟 Standardisation des colonnes (conversion dynamique)
        if dataset == "covid":
            df = df.rename(columns={
                "Country": "country",
                "Date_reported": "date",
                "New_cases": "cases",
                "New_deaths": "deaths"
            })
        elif dataset == "mpox":
            df = df.rename(columns={
                "location": "country",
                "date": "date",
                "new_cases": "cases",
                "total_deaths": "deaths"
            })
        
        # 🌟 Vérification et correction des types de données
        df["date"] = pd.to_datetime(df["date"], errors='coerce')  # Convertir en datetime
        df["cases"] = pd.to_numeric(df["cases"], errors='coerce').fillna(0).astype(int)
        df["deaths"] = pd.to_numeric(df["deaths"], errors='coerce').fillna(0).astype(int)

        # 🌟 Suppression des valeurs invalides
        df = df.dropna(subset=["date"])  # Supprimer les dates invalides
        df = df[df["cases"] >= 0]  # Supprimer les valeurs négatives
        df = df[df["deaths"] >= 0]

        # 🌟 Sauvegarde des fichiers nettoyés
        cleaned_file = os.path.join(DATA_FOLDER, f"{dataset}_cleaned.csv")
        df[STANDARD_COLUMNS].to_csv(cleaned_file, index=False)
        cleaned_files[dataset] = cleaned_file

        print(f"✅ Données nettoyées et sauvegardées dans {cleaned_file}")

    return cleaned_files


# 📌 Étape 2 : Charger les données dans PostgreSQL
@task
def load_to_postgres(cleaned_files):
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
    
    # 📌 Création des tables génériques
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pandemic_data (
            id SERIAL PRIMARY KEY, 
            country VARCHAR(100), 
            date DATE, 
            cases INT, 
            deaths INT, 
            disease VARCHAR(50)
        );
    """)

    # 📌 Insertion dynamique des données nettoyées
    for dataset, file_path in cleaned_files.items():
        df = pd.read_csv(file_path)

        for _, row in df.iterrows():
            print(f"Insertion : {row['country']} | {row['date']} | {row['cases']} | {row['deaths']} | {dataset}")
            cursor.execute("""
                INSERT INTO pandemic_data (country, date, cases, deaths, disease) 
                VALUES (%s, %s, %s, %s, %s)
            """, (row["country"], row["date"], row["cases"], row["deaths"], dataset))

    conn.commit()
    cursor.close()
    conn.close()

    print("✅ Données chargées dans PostgreSQL")

# 📌 Étape 3 : Définition du flow Prefect
@flow
def etl_pipeline():
    cleaned_files = clean_data()
    load_to_postgres(cleaned_files)

# 📌 Exécuter le pipeline
if __name__ == "__main__":
    etl_pipeline()
