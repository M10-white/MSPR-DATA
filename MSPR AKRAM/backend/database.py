# backend/database.py

# Importe les fonctions et classes nécessaires de SQLAlchemy pour la création de moteurs de base de données et de sessions.
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# Importe la classe de base des modèles de la base de données définis dans 'models.py'.
from models import Base
# Importe le module os pour interagir avec les variables d'environnement.
import os
# Importe load_dotenv pour charger les variables d'environnement à partir d'un fichier .env.
from dotenv import load_dotenv

# Charger les variables d'environnement au démarrage de l'application.
load_dotenv()

# --- Configuration de la Base de Données ---
# Récupère l'URL de la base de données à partir des variables d'environnement.
# Si la variable DATABASE_URL n'est pas définie, utilise 'sqlite:///./mspr.db' par défaut (base de données SQLite locale).
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mspr.db")

# Crée le moteur SQLAlchemy.
# Ce moteur est responsable de la connexion à la base de données.
# Pour SQLite, 'check_same_thread': False est nécessaire pour permettre à plusieurs threads d'interagir avec la base de données.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Crée la classe SessionLocal.
# Une instance de SessionLocal sera une session de base de données.
# autocommit=False: Les changements ne sont pas committés automatiquement.
# autoflush=False: Les objets ne sont pas flushés automatiquement dans la base de données.
# bind=engine: Lie la session au moteur de base de données créé ci-dessus.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Redéfinit Base ici, si elle a été importée, pour s'assurer qu'elle est bien la base déclarative pour SQLAlchemy.
# Bien que déjà importée depuis models.py, cette ligne assure la cohérence ou permet de gérer des cas où Base ne serait pas directement accessible.
Base = declarative_base()

# --- Dépendance de Base de Données pour FastAPI ---
# Cette fonction est une dépendance FastAPI qui gère le cycle de vie de la session de base de données.
# Elle fournit une session de base de données à la requête et s'assure qu'elle est fermée après la requête.
def get_db():
    db = SessionLocal() # Crée une nouvelle session de base de données.
    try:
        yield db # Fournit la session à la route FastAPI qui la demande.
    finally:
        db.close() # Ferme la session de base de données après que la requête est terminée (même en cas d'erreur).

# --- Initialisation de la Base de Données ---
# Cette fonction est appelée au démarrage de l'application FastAPI (voir main.py).
# Elle crée toutes les tables définies dans les modèles SQLAlchemy si elles n'existent pas déjà dans la base de données.
def init_db():
    Base.metadata.create_all(bind=engine) # Crée les tables en se basant sur les métadonnées des modèles et le moteur de base de données.