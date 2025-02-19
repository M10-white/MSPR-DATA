from fastapi import FastAPI
import pandas as pd
import joblib

app = FastAPI()

# Charger le modèle
covid_model = joblib.load("covid_model.pkl")
mpox_model = joblib.load("mpox_model.pkl")

@app.get("/predict/")
def predict(country: str, disease: str):
    if disease == "covid":
        model = covid_model
    elif disease == "mpox":
        model = mpox_model
    else:
        return {"error": "Maladie inconnue"}

    future_df = pd.DataFrame({"ds": pd.date_range(start="2025-02-05", periods=30)})
    forecast = model.predict(future_df)

    return {"predictions": forecast[["ds", "yhat"]].to_dict(orient="records")}
