from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Data, Base
import os

# Configuration de la base de données (assurez-vous que c'est le même que dans database.py)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'mspr.db')
DB_URL = f'sqlite:///{DB_PATH}'

engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
session = Session()

def get_unique_countries():
    # Assurez-vous que la table est créée avant de l'interroger (si vous ne l'avez pas déjà fait)
    Base.metadata.create_all(bind=engine)
    countries = session.query(Data.country).distinct().all()
    return sorted([c[0] for c in countries])

if __name__ == '__main__':
    print("Récupération des pays uniques de la base de données...")
    unique_countries = get_unique_countries()
    print("Pays uniques trouvés :")
    for country in unique_countries:
        print(f"- {country}")
    session.close() 