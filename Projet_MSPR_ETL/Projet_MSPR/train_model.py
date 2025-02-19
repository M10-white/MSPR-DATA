import pandas as pd
import matplotlib.pyplot as plt
import os
import joblib
from sqlalchemy import create_engine
from prophet import Prophet
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# 📌 Connexion à PostgreSQL
DATABASE_URL = "postgresql://postgres:admin@localhost:5432/pandemics"
engine = create_engine(DATABASE_URL)

# 📌 Charger les données depuis PostgreSQL
def load_data():
    query = "SELECT country, date, cases, deaths, disease FROM pandemic_data"
    df = pd.read_sql(query, engine)
    
    # 🌟 Conversion des types
    df["date"] = pd.to_datetime(df["date"])
    df["cases"] = pd.to_numeric(df["cases"], errors='coerce').fillna(0).astype(int)
    df["deaths"] = pd.to_numeric(df["deaths"], errors='coerce').fillna(0).astype(int)
    
    # 🌟 Trier les données
    df = df.sort_values(by=["country", "date"])
    
    print("✅ Données chargées et nettoyées !")
    return df

# 📌 Prédire les cas futurs avec Prophet
def predict_cases(df, country="France", disease="covid"):
    print(f"📊 Prédiction des cas de {disease} pour {country}...")

    # 🌟 Filtrer les données
    df_train = df[(df["country"] == country) & (df["disease"] == disease)][["date", "cases"]]
    df_train = df_train.rename(columns={"date": "ds", "cases": "y"})

    if df_train.empty:
        print(f"⚠️ Pas de données pour {country} - {disease}")
        return

    # 📌 Vérifier si un modèle entraîné existe déjà
    model_filename = f"{disease}_model.pkl"
    if os.path.exists(model_filename):
        model = joblib.load(model_filename)
        print(f"📥 Modèle Prophet chargé depuis {model_filename}")
    else:
        # 🌟 Entraîner Prophet
        model = Prophet()
        model.fit(df_train)

        # 🌟 Sauvegarder le modèle
        joblib.dump(model, model_filename)
        print(f"💾 Modèle Prophet sauvegardé sous {model_filename}")

    # 🌟 Prédire les 6 prochains mois
    future = model.make_future_dataframe(periods=180)
    forecast = model.predict(future)

    # 🌟 Afficher le résultat
    plt.figure(figsize=(10,5))
    model.plot(forecast)
    plt.title(f"Prédiction des cas {disease.upper()} pour {country}")
    plt.show()

# 📌 Classifier les explosions de cas avec XGBoost
def classify_risk(df, disease="covid"):
    print(f"🎯 Classification des risques pour {disease}...")

    df_disease = df[df["disease"] == disease].copy()  # ✅ Correction du warning de copie

    # 🌟 Détection des pics (augmentation brutale des cas)
    df_disease["explosion_cas"] = (df_disease["cases"].diff().fillna(0) > 500).astype(int)

    # 🌟 Préparation des features
    X = df_disease[["cases", "deaths"]]
    y = df_disease["explosion_cas"]

    # 🌟 Séparation train/test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 📌 Vérifier si un modèle entraîné existe déjà
    model_filename = f"{disease}_xgb.pkl"
    if os.path.exists(model_filename):
        model_xgb = joblib.load(model_filename)
        print(f"📥 Modèle XGBoost chargé depuis {model_filename}")
    else:
        # 🌟 Entraînement XGBoost
        model_xgb = XGBClassifier(use_label_encoder=False, eval_metric="logloss")
        model_xgb.fit(X_train, y_train)

        # 🌟 Sauvegarder le modèle
        joblib.dump(model_xgb, model_filename)
        print(f"💾 Modèle XGBoost sauvegardé sous {model_filename}")

    # 🌟 Prédiction et évaluation
    y_pred = model_xgb.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"✅ Précision du modèle {disease.upper()} : {accuracy:.2f}")

# 📌 Exécuter l'entraînement
if __name__ == "__main__":
    df = load_data()
    predict_cases(df, country="France", disease="covid")
    predict_cases(df, country="France", disease="mpox")
    classify_risk(df, disease="covid")
    classify_risk(df, disease="mpox")
