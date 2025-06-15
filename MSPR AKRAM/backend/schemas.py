from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, date

# --- Schémas pour les Utilisateurs ---

# UserBase: Schéma de base pour les utilisateurs, définissant les champs communs.
class UserBase(BaseModel):
    username: str # Nom d'utilisateur (chaîne de caractères).
    email: EmailStr # Adresse email, validée comme un format d'email standard.
    country: str # Pays de l'utilisateur.

# UserCreate: Schéma utilisé pour la création d'un nouvel utilisateur.
# Hérite de UserBase et ajoute le champ 'password'.
class UserCreate(UserBase):
    password: str # Mot de passe en clair (sera haché avant stockage).

# UserOut: Schéma pour la sortie (réponse) des informations utilisateur.
# Hérite de UserBase et ajoute des champs générés par le système.
class UserOut(UserBase):
    id: int # ID unique de l'utilisateur.
    is_admin: bool # Statut d'administrateur (booléen).
    created_at: datetime # Date et heure de création du compte.
    
    # Configuration interne de Pydantic pour mapper les attributs des objets SQLAlchemy aux champs Pydantic.
    class Config:
        from_attributes = True # Ancien `orm_mode = True` pour la compatibilité avec SQLAlchemy.

# --- Schémas pour les Données COVID-19 ---

# DataIn: Schéma pour l'entrée de données COVID-19 (lors de l'ajout de nouvelles données).
class DataIn(BaseModel):
    date: date # Date de l'enregistrement.
    country: str # Pays concerné.
    confirmed: int # Nombre de cas confirmés.
    deaths: int # Nombre de décès.
    recovered: int # Nombre de cas guéris.
    new_cases: int # Nombre de nouveaux cas.
    new_deaths: int # Nombre de nouveaux décès.
    new_recovered: int # Nombre de nouveaux cas guéris.

# DataOut: Schéma pour la sortie (réponse) des données COVID-19.
# Hérite de DataIn et ajoute le champ 'id' généré par la base de données.
class DataOut(DataIn):
    id: int # ID unique de l'entrée de données.

    # Configuration pour le mappage avec les attributs SQLAlchemy.
    class Config:
        from_attributes = True

# --- Schémas pour la Prédiction IA ---

# PredictionIn: Schéma pour l'entrée des paramètres de la prédiction IA.
class PredictionIn(BaseModel):
    country: str # Pays pour lequel la prédiction est demandée.
    future_date: date # Date future pour laquelle la prédiction est demandée.
    # region: str # Commenté: Pourrait être utilisé pour des prédictions plus granulaires (future extension).
    # location: str # Commenté: Idem.
    # construction: str # Commenté: Idem.
    # value: float # Commenté: Idem.

# PredictionOut: Schéma pour la sortie (réponse) de la prédiction IA.
class PredictionOut(BaseModel):
    prediction: float # La valeur prédite (ex: nombre de cas).
    score: float # Un score de confiance ou de performance du modèle (exemple: 0.8).

# --- Schémas pour l'Authentification (Jetons) ---

# Token: Schéma pour la réponse d'un jeton d'accès après connexion.
class Token(BaseModel):
    access_token: str # Le jeton d'accès JWT.
    token_type: str # Le type de jeton (généralement "bearer").

# TokenData: Schéma pour les données contenues dans un jeton JWT.
class TokenData(BaseModel):
    username: Optional[str] = None # Le nom d'utilisateur stocké dans le jeton (peut être nul si non présent). 