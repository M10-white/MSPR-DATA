import csv
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Data
import pandas as pd # Importez pandas

DB_URL = 'sqlite:///mspr.db'
CSV_PATH = 'data/covid_cleaned.csv'

engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)

def parse_int(value):
    try:
        return int(value)
    except:
        return 0

def parse_float(value):
    try:
        return float(value)
    except:
        return 0.0

def parse_date(value):
    try:
        return datetime.strptime(value, '%Y-%m-%d')
    except:
        return None

def import_csv():
    session = Session()
    try:
        # Lire le CSV avec pandas
        df = pd.read_csv(CSV_PATH)

        # Convertir la colonne 'date' au format datetime
        df['date'] = pd.to_datetime(df['date'])

        # S'assurer que les colonnes sont des types numériques, gérer les erreurs
        # Utilise 'cases' du CSV pour 'confirmed' dans le modèle
        df['cases'] = pd.to_numeric(df['cases'], errors='coerce').fillna(0).astype(int)
        df['deaths'] = pd.to_numeric(df['deaths'], errors='coerce').fillna(0).astype(int)
        df['recovered'] = pd.to_numeric(df['recovered'], errors='coerce').fillna(0).astype(int)

        # Trier les données pour le calcul des différences
        df = df.sort_values(by=['country', 'date'])

        # Calculer les nouvelles colonnes (new_cases, new_deaths, new_recovered)
        df['new_cases'] = df.groupby('country')['cases'].diff().fillna(0).astype(int) # Basé sur 'cases' du CSV
        df['new_deaths'] = df.groupby('country')['deaths'].diff().fillna(0).astype(int)
        df['new_recovered'] = df.groupby('country')['recovered'].diff().fillna(0).astype(int)

        # S'assurer que les nouvelles valeurs ne sont pas négatives (cas où les données sont corrigées à la baisse)
        df['new_cases'] = df['new_cases'].apply(lambda x: max(0, x))
        df['new_deaths'] = df['new_deaths'].apply(lambda x: max(0, x))
        df['new_recovered'] = df['new_recovered'].apply(lambda x: max(0, x))

        # Supprimer les données existantes pour un import propre
        session.query(Data).delete()
        session.commit()

        # Insérer les données du DataFrame dans la base de données
        for _, row in df.iterrows():
            data = Data(
                country=row['country'],
                date=row['date'],
                confirmed=row['cases'], # Utilise 'cases' du CSV pour le champ 'confirmed' du modèle
                deaths=row['deaths'],
                recovered=row['recovered'],
                new_cases=row['new_cases'],
                new_deaths=row['new_deaths'],
                new_recovered=row['new_recovered']
            )
            session.add(data)
        session.commit()
        print('Import terminé avec calcul des nouvelles données !')
    except Exception as e:
        session.rollback()
        print(f"Erreur lors de l'importation : {e}")
    finally:
        session.close()

if __name__ == '__main__':
    # S'assurer que les tables sont créées avant l'importation
    Base.metadata.create_all(bind=engine)
    import_csv() 