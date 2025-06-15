# backend/models.py

# Importe les types de colonnes de SQLAlchemy pour définir le schéma de la base de données.
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean
# Importe `declarative_base` pour créer une classe de base déclarative pour les modèles SQLAlchemy.
from sqlalchemy.ext.declarative import declarative_base
# Importe le module datetime pour gérer les dates et heures.
import datetime

# Crée une instance de la base déclarative. Tous les modèles de la base de données hériteront de cette classe.
Base = declarative_base()

# --- Modèle User (Utilisateurs) ---
# Représente la table 'users' dans la base de données.
class User(Base):
    __tablename__ = "users" # Définit le nom de la table dans la base de données.

    # Colonnes de la table 'users':
    id = Column(Integer, primary_key=True, index=True) # Clé primaire auto-incrémentée et indexée.
    username = Column(String, unique=True, index=True, nullable=False) # Nom d'utilisateur, doit être unique, indexé et non nul.
    email = Column(String, unique=True, index=True, nullable=False) # Adresse email, doit être unique, indexée et non nulle.
    hashed_password = Column(String, nullable=False) # Mot de passe haché, non nul.
    created_at = Column(DateTime, default=datetime.datetime.utcnow) # Date et heure de création de l'utilisateur, avec une valeur par défaut.
    country = Column(String, nullable=False) # Pays de l'utilisateur, non nul (lié aux règles RGPD).
    is_admin = Column(Boolean, default=False) # Indique si l'utilisateur est un administrateur, par défaut False.

# --- Modèle Data (Données COVID-19) ---
# Représente la table 'data' dans la base de données, stockant les informations sur la pandémie.
class Data(Base):
    __tablename__ = "data" # Définit le nom de la table dans la base de données.

    # Colonnes de la table 'data':
    id = Column(Integer, primary_key=True, index=True) # Clé primaire auto-incrémentée et indexée.
    country = Column(String, index=True) # Pays associé à la donnée, indexé pour des recherches rapides.
    date = Column(DateTime) # Date de l'enregistrement de la donnée.
    confirmed = Column(Integer) # Nombre de cas confirmés.
    deaths = Column(Integer) # Nombre de décès.
    recovered = Column(Integer) # Nombre de cas guéris.
    new_cases = Column(Integer) # Nombre de nouveaux cas (calculé ou fourni).
    new_deaths = Column(Integer) # Nombre de nouveaux décès (calculé ou fourni).
    new_recovered = Column(Integer) # Nombre de nouveaux cas guéris (calculé ou fourni). 