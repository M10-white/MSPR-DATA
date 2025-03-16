import os
import pickle
import pandas as pd
import psycopg2
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error

# 📌 Dossier de stockage
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Chemin absolu du script
DATA_FOLDER = os.path.join(BASE_DIR, "data")

# 📌 Vérification du dossier de stockage
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

# 📌 Connexion PostgreSQL
def get_db_connection():
    return psycopg2.connect(
        dbname="pandemics",
        user="postgres",
        password="admin",
        host="localhost",
        port=5432
    )

# 📌 Extraction des données
def fetch_pandemic_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT date, country, cases, deaths, recovered, active, mortality_rate, recovery_rate
        FROM pandemic_data
        WHERE cases > 0
        ORDER BY date ASC;
    """)

    columns = ["date", "country", "cases", "deaths", "recovered", "active", "mortality_rate", "recovery_rate"]
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    df = pd.DataFrame(data, columns=columns)
    df["date"] = pd.to_datetime(df["date"])  # Conversion en format datetime
    return df

# 📌 Prétraitement des données
def preprocess_data(df, country):
    df = df[df["country"] == country].copy()
    
    # Transformation des dates en jours écoulés depuis la première observation
    df["days_since_start"] = (df["date"] - df["date"].min()).dt.days

    # Définition des features
    features = ["days_since_start", "deaths", "recovered", "active", "mortality_rate", "recovery_rate"]
    
    # Suppression des valeurs manquantes
    df = df.dropna(subset=features + ["cases"])

    # Définition des variables X (features) et y (cible)
    X = df[features]
    y = df["cases"]

    return X, y

# 📌 Entraînement du modèle et sauvegarde
def train_model(country="France"):
    df = fetch_pandemic_data()
    
    if df.empty or country not in df["country"].unique():
        raise ValueError(f"Aucune donnée disponible pour {country}")

    X, y = preprocess_data(df, country)

    # Séparation des données (80% entraînement, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Création et entraînement du modèle
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Évaluation
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    # 📌 Enregistrement du modèle dans le dossier `data`
    model_filename = os.path.join(DATA_FOLDER, f"model_{country.lower()}.pkl")
    with open(model_filename, "wb") as f:
        pickle.dump(model, f)

    print(f"✅ Modèle entraîné et sauvegardé : {model_filename}")
    print(f"📊 MAE: {mae:.2f} | RMSE: {rmse:.2f}")

if __name__ == "__main__":
    train_model("France")  # Entraîner un modèle pour la France
