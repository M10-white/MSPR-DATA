from fastapi import APIRouter, HTTPException
from app.services.load_data import load_csv_data

router = APIRouter()

# Charger les données CSV
covid_data, country_data = load_csv_data()

@router.get("/covid-data")
def get_covid_data():
    if covid_data.empty:
        raise HTTPException(status_code=404, detail="No COVID data found")
    return covid_data.to_dict(orient='records')

@router.get("/country-data")
def get_country_data():
    if country_data.empty:
        raise HTTPException(status_code=404, detail="No country data found")
    return country_data.to_dict(orient='records')