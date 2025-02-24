from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import joblib
import os
from sqlalchemy import create_engine
from prophet import Prophet
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# -------------------------------
# Configuration de CORS et de l'app
# -------------------------------
app = FastAPI(title="COVID-19 & Pandemic API")

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

# -------------------------------
# Connexion à la base de données PostgreSQL
# -------------------------------
DATABASE_URL = "postgresql://postgres:admin@localhost:5432/pandemics"
engine = create_engine(DATABASE_URL)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#DATA_FOLDER = os.path.join(BASE_DIR, "..", "..", "Projet_MSPR_ETL", "Projet_MSPR", "data")
DATA_FOLDER = os.path.join("..","..","Projet_MSPR_ETL", "Projet_MSPR", "data")
COVID_CSV = os.path.join(DATA_FOLDER, "covid_cleaned.csv")

def load_data():
    """
    Charge et prépare les données depuis la table 'pandemic_data' dans PostgreSQL.
    """
    query = "SELECT country, date, cases, deaths, disease FROM pandemic_data"
    df = pd.read_sql(query, engine)
    df["date"] = pd.to_datetime(df["date"])
    df["cases"] = pd.to_numeric(df["cases"], errors="coerce").fillna(0).astype(int)
    df["deaths"] = pd.to_numeric(df["deaths"], errors="coerce").fillna(0).astype(int)
    df = df.sort_values(by=["country", "date"])
    return df

# -------------------------------
# Fonctions de gestion des modèles
# -------------------------------
def get_prophet_model(df: pd.DataFrame, country: str, disease: str):
    """
    Charge (ou entraîne) un modèle Prophet pour un pays et une maladie donnés.
    """
    # Filtrer les données pour le pays et la maladie
    df_train = df[(df["country"] == country) & (df["disease"] == disease)][["date", "cases"]]
    if df_train.empty:
        return None, "Aucune donnée disponible pour ce pays et cette maladie."
    
    # Préparer les données pour Prophet
    df_train = df_train.rename(columns={"date": "ds", "cases": "y"})
    
    model_filename = f"{disease}_model.pkl"
    if os.path.exists(model_filename):
        model = joblib.load(model_filename)
        print(f"Modèle Prophet chargé depuis {model_filename}")
    else:
        model = Prophet()
        model.fit(df_train)
        joblib.dump(model, model_filename)
        print(f"Modèle Prophet entraîné et sauvegardé sous {model_filename}")
    return model, None

def get_xgboost_model(df: pd.DataFrame, disease: str):
    """
    Charge (ou entraîne) un modèle XGBoost pour classifier le risque d'explosion des cas.
    """
    df_disease = df[df["disease"] == disease].copy()
    if df_disease.empty:
        return None, "Aucune donnée disponible pour cette maladie."
    
    # Définir une explosion de cas (augmentation brutale supérieure à 500)
    df_disease["explosion_cas"] = (df_disease["cases"].diff().fillna(0) > 500).astype(int)
    X = df_disease[["cases", "deaths"]]
    y = df_disease["explosion_cas"]
    
    # Séparation train/test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model_filename = f"{disease}_xgb.pkl"
    if os.path.exists(model_filename):
        model_xgb = joblib.load(model_filename)
        print(f"Modèle XGBoost chargé depuis {model_filename}")
    else:
        model_xgb = XGBClassifier(use_label_encoder=False, eval_metric="logloss")
        model_xgb.fit(X_train, y_train)
        joblib.dump(model_xgb, model_filename)
        print(f"Modèle XGBoost entraîné et sauvegardé sous {model_filename}")
    
    accuracy = accuracy_score(y_test, model_xgb.predict(X_test))
    return model_xgb, accuracy

# -------------------------------
# Endpoints API existants
# -------------------------------
@app.get("/")
def read_root():
    return {"message": "Welcome to the COVID-19 API"}

@app.get("/api/v1/covid-data")
def get_covid_data():
    """
    Retourne les données COVID réelles en lisant le fichier CSV nettoyé.
    Le CSV doit contenir au minimum des colonnes telles que : date, cases et deaths.
    """
    if not os.path.exists(COVID_CSV):
        raise HTTPException(status_code=404, detail="Fichier de données COVID introuvable.")
    
    try:
        # Lecture du CSV
        df = pd.read_csv(COVID_CSV)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la lecture du CSV : {e}")

    # Conversion de la colonne 'date' en datetime (si présente)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    
    # Retourne les données sous forme de liste de dictionnaires
    return df.to_dict(orient="records")

@app.get("/api/v1/country-data")
def get_country_data():
    # Exemple de données statiques – à remplacer par votre logique d'extraction réelle
    country_data = [
        {"name": "France", "transmission_rate": 1.2, "mortality": 0.02, "region": "Europe"},
        {"name": "USA", "transmission_rate": 1.5, "mortality": 0.03, "region": "North America"},
    ]
    return country_data

# -------------------------------
# Nouveaux endpoints pour le modèle
# -------------------------------
@app.get("/api/v1/predict")
def predict(country: str, disease: str, periods: int = 30):
    """
    Prédit les cas futurs pour un pays et une maladie donnée en utilisant Prophet.
    
    - **country**: nom du pays (ex: France)
    - **disease**: nom de la maladie (ex: covid ou mpox)
    - **periods**: nombre de jours à prédire (par défaut 30)
    """
    df = load_data()
    model, error = get_prophet_model(df, country, disease)
    if error:
        raise HTTPException(status_code=404, detail=error)
    
    # Déterminer la dernière date connue dans les données
    last_date = df["date"].max()
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    
    # Filtrer pour ne renvoyer que les prédictions postérieures à la dernière date
    forecast_future = forecast[forecast["ds"] > last_date]
    predictions = forecast_future[["ds", "yhat"]].to_dict(orient="records")
    
    return {
        "country": country,
        "disease": disease,
        "last_date": last_date.strftime("%Y-%m-%d"),
        "predictions": predictions
    }

@app.get("/api/v1/classify")
def classify(disease: str):
    """
    Classifie le risque d'explosion des cas pour une maladie donnée en utilisant XGBoost
    et renvoie la précision du modèle.
    
    - **disease**: nom de la maladie (ex: covid ou mpox)
    """
    df = load_data()
    model, result = get_xgboost_model(df, disease)
    if model is None:
        raise HTTPException(status_code=404, detail=result)
    
    return {"disease": disease, "accuracy": result}

# -------------------------------
# Lancement de l'application
# -------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
    import os
print("Répertoire de travail courant :", os.getcwd())
