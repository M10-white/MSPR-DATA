from prefect import flow, task
import pandas as pd
import os
import psycopg2
import time
from sklearn.model_selection import train_test_split


# 📌 Dossier de stockage
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Récupère le chemin absolu du script
DATA_FOLDER = os.path.join(BASE_DIR, "data")
CSV_FILE = os.path.join(DATA_FOLDER, "covid_19_clean_complete.csv")
CLEANED_CSV = os.path.join(DATA_FOLDER, "covid_cleaned.csv")

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

# 📌 Analyse complète des données
def analyze_data(df, title="Analyse des données"):
    print(f"\n🔍 {title}")
    print("-" * 40)
    
    print(f"Nombre total de lignes et de colonnes : {df.shape}")
    print("📋 Colonnes dans le fichier CSV :", df.columns.values) 
     
    print("Types des données :")
    print(df.dtypes)
    print("\nNombre de valeurs nulles par colonne :")
    print(df.isnull().sum())
    total_nan = df.isnull().sum().sum()
    print(f"\nNombre total de valeurs NaN : {total_nan}")

    numeric_cols = ["cases", "deaths", "recovered", "active"]
    for col in numeric_cols:
        if col in df.columns:
            print(f"Valeurs négatives dans '{col}' : {(df[col] < 0).sum()}")

    if all(col in df.columns for col in ["cases", "deaths", "recovered", "active"]):
        print("\nIncohérences détectées :")
        print(f"Valeurs incohérentes dans 'recovered' : {(df['recovered'] > (df['cases'] - df['deaths'])).sum()}")
        print(f"Nombre de lignes avec 'cases' <= 0 : {(df['cases'] <= 0).sum()}")
    print("-" * 40)

# 📌 EXTRACT : Chargement des données brutes
@task
def extract_data():
    if not os.path.exists(CSV_FILE):
        raise FileNotFoundError(f"❌ Le fichier {CSV_FILE} est introuvable.")
    print(f"📂 Chargement du fichier {CSV_FILE}...")

    df = pd.read_csv(CSV_FILE, encoding="utf-8", delimiter=",", on_bad_lines="skip")
    
    print("\n🧾 Données brutes (avant renommage des colonnes) :")
    print(df.head()) 

    df.rename(columns={
        "Province/State": "province_state",
        "Country/Region": "country",
        "Lat": "latitude",
        "Long": "longitude",
        "Date": "date",
        "Confirmed": "cases",
        "Deaths": "deaths",
        "Recovered": "recovered",
        "Active": "active",
        "WHO Region": "who_region"
    }, inplace=True)

    analyze_data(df, "Analyse AVANT transformation")
    return df

# 📌 TRANSFORM : Nettoyage et transformation des données
@task
def transform_data(df):
    # 🧹 Suppression de la colonne 'province_state' si elle existe (inutile pour l'analyse globale)
    df.drop(columns=["province_state"], inplace=True, errors="ignore")

    # 📅 Conversion de la colonne 'date' en type datetime, en ignorant les erreurs
    df["date"] = pd.to_datetime(df["date"], errors='coerce')

    # 🔢 Conversion des colonnes numériques en type entier, en remplaçant les valeurs invalides par 0
    for col in ["cases", "deaths", "recovered"]:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    # 🔄 Correction des valeurs incohérentes : 
    # 'recovered' ne peut pas être supérieur à 'cases - deaths', sinon on ajuste.
    df["recovered"] = df.apply(lambda row: min(row["recovered"], row["cases"] - row["deaths"]), axis=1)

    # 📉 Calcul de la colonne 'active' : cas actifs = cas totaux - décès - guérisons
    df["active"] = df["cases"] - df["deaths"] - df["recovered"]

    # ✅ Correction des cas actifs négatifs (remplacement par 0 si inférieur)
    df["active"] = df["active"].apply(lambda x: max(0, x))

    # 📊 Calcul des taux :
    # - Taux de mortalité : (décès / cas) * 100 (limité à 100)
    # - Taux de récupération : (guérisons / cas) * 100 (limité à 100)
    df["mortality_rate"] = (df["deaths"] / df["cases"]).fillna(0).apply(lambda x: min(100, x * 100))
    df["recovery_rate"] = (df["recovered"] / df["cases"]).fillna(0).apply(lambda x: min(100, x * 100))

    # 🗑️ Suppression des lignes où le nombre de cas est inférieur ou égal à zéro
    df = df[df["cases"] > 0]

    # 🔍 Analyse des données après transformation pour vérifier la cohérence
    analyze_data(df, "Analyse APRÈS transformation")

    # 📌 Préparation des données pour un modèle de prédiction
    # Transformation des dates en jours écoulés depuis la première observation
    df["days_since_start"] = (df["date"] - df["date"].min()).dt.days

    # Définition des features et de la cible
    features = ["days_since_start", "deaths", "recovered", "active", "mortality_rate", "recovery_rate"]
    df = df.dropna(subset=features + ["cases"])  # Suppression des valeurs manquantes

    X = df[features]  # Features
    y = df["cases"]  # Cible

    # 🔀 Séparation des données (60% entraînement, 20% validation, 20% test)
    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.4, random_state=42)  # 40% pour val/test
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)  # 20% val / 20% test

    print(f"📊 Répartition des données :\n"
          f"- Entraînement : {len(X_train)} échantillons\n"
          f"- Validation : {len(X_val)} échantillons\n"
          f"- Test : {len(X_test)} échantillons")

    # 📤 Retourne à la fois le DataFrame transformé pour le chargement en BDD et les ensembles de données pour le modèle
    return df

# 📌 LOAD : Sauvegarde et chargement en base de données
@task
def load_to_postgres(df):
    """ Charge les données nettoyées dans PostgreSQL. """
    if df.empty:
        raise ValueError("❌ Les données transformées sont vides, arrêt du chargement.")

    # 📂 Sauvegarde du fichier nettoyé
    df.to_csv(CLEANED_CSV, index=False)
    print(f"✅ Données nettoyées sauvegardées dans {CLEANED_CSV}")

    # 🔍 Vérification de la connexion à PostgreSQL
    if not check_postgres():
        raise ConnectionError("Échec de connexion à PostgreSQL.")

    # 📌 Création des tables et récupération de l'utilisateur
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

    # 📌 Insertion des données dans la base
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO pandemic_data (user_id, country, latitude, longitude, date, cases, deaths, recovered, active, who_region, mortality_rate, recovery_rate) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (country, date, user_id) DO UPDATE SET 
                cases = EXCLUDED.cases, deaths = EXCLUDED.deaths, recovered = EXCLUDED.recovered,
                active = EXCLUDED.active, who_region = EXCLUDED.who_region, 
                mortality_rate = EXCLUDED.mortality_rate, recovery_rate = EXCLUDED.recovery_rate;
        """, (user_id, row["country"], row["latitude"], row["longitude"], row["date"], row["cases"], row["deaths"], row["recovered"], row["active"], row["who_region"], row["mortality_rate"], row["recovery_rate"]))

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Données chargées dans PostgreSQL avec succès !")

# 📌 FLOW : Orchestration du pipeline ETL
@flow
def etl_pipeline():
    df_raw = extract_data()
    df_cleaned = transform_data(df_raw)
    load_to_postgres(df_cleaned)

# 📌 Exécution du pipeline
if __name__ == "__main__":
    etl_pipeline()
