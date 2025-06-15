from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
import schemas
import models
import database
import auth
from typing import List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()

# Authentification
@router.post("/register", response_model=schemas.UserOut)
def register(
    user: schemas.UserCreate, # Reçoit les données de l'utilisateur à créer, validées par le schéma UserCreate.
    db: Session = Depends(database.get_db) # Injecte une session de base de données.
):
    """Enregistre un nouvel utilisateur dans la base de données.
    Vérifie si le nom d'utilisateur ou l'email existe déjà pour éviter les doublons.
    Hache le mot de passe avant de sauvegarder l'utilisateur."""
    # Vérifie si un utilisateur avec le même nom d'utilisateur ou email existe déjà.
    db_user = db.query(models.User).filter((models.User.username == user.username) | (models.User.email == user.email)).first()
    if db_user:
        # Lève une exception HTTP 400 si l'utilisateur existe déjà.
        raise HTTPException(status_code=400, detail="Username or email already registered")
    
    # Hache le mot de passe avant de le stocker dans la base de données.
    hashed_password = auth.get_password_hash(user.password)
    # Crée une nouvelle instance du modèle User avec les données fournies.
    new_user = models.User(username=user.username, email=user.email, hashed_password=hashed_password, country=user.country, is_admin=False)
    
    # Ajoute le nouvel utilisateur à la session de la base de données, commite et rafraîchit l'objet.
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user # Retourne l'utilisateur créé, conformément au schéma UserOut.

# Utilisateur courant
@router.get("/me", response_model=schemas.UserOut)
def read_users_me(
    current_user: models.User = Depends(auth.get_current_user) # Dépendance qui valide le jeton JWT et retourne l'utilisateur authentifié.
):
    """Récupère les informations de l'utilisateur actuellement authentifié.
    Cette route nécessite un jeton JWT valide."""
    logger.debug(f'current_user (from auth.get_current_user): {current_user.__dict__}')
    # Force la conversion du champ 'is_admin' en booléen pour s'assurer de la cohérence du type.
    user_dict = current_user.__dict__.copy()
    user_dict['is_admin'] = bool(user_dict.get('is_admin', False))
    return schemas.UserOut(**user_dict) # Retourne les informations de l'utilisateur sous le format UserOut.

# Données historiques
@router.post("/data", response_model=schemas.DataOut)
def add_data(
    data: schemas.DataIn, # Données COVID-19 à ajouter, validées par le schéma DataIn.
    db: Session = Depends(database.get_db), # Injecte une session de base de données.
    current_user: models.User = Depends(auth.get_current_user) # Assure que seul un utilisateur authentifié peut ajouter des données.
):
    """Ajoute de nouvelles entrées de données COVID-19 à la base de données.
    Requiert une authentification préalable."""
    # Crée une nouvelle instance du modèle Data avec les données reçues.
    db_data = models.Data(**data.dict())
    
    # Ajoute les données à la session de la base de données, commite et rafraîchit l'objet.
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data # Retourne les données ajoutées, conformément au schéma DataOut.

@router.get("/data", response_model=List[schemas.DataOut])
def read_data(
    country: Optional[str] = Query(None), # Paramètre de requête facultatif pour filtrer les données par pays.
    skip: int = 0, # Paramètre pour la pagination : nombre d'éléments à ignorer.
    limit: int = 10000, # Paramètre pour la pagination : nombre maximal d'éléments à retourner.
    db: Session = Depends(database.get_db) # Injecte une session de base de données.
):
    """Récupère les données historiques de la pandémie. Peut être filtré par pays et paginé.
    Accessible publiquement (pas de dépendance d'authentification)."""
    query = db.query(models.Data)
    if country:
        query = query.filter(models.Data.country == country) # Applique le filtre par pays si spécifié.
    # Exécute la requête avec les paramètres de pagination et retourne tous les résultats.
    data = query.offset(skip).limit(limit).all()
    return data # Retourne une liste d'objets DataOut.

# Récupérer tous les pays uniques
@router.get("/countries", response_model=List[str])
def get_all_countries(
    db: Session = Depends(database.get_db) # Injecte une session de base de données.
):
    """Récupère une liste de tous les pays uniques présents dans les données COVID-19.
    Les pays sont triés par ordre alphabétique. Accessible publiquement."""
    # Récupère les noms de pays distincts et les trie.
    countries = db.query(models.Data.country).distinct().order_by(models.Data.country).all()
    return [country[0] for country in countries] # Retourne une liste de chaînes de caractères (noms de pays).

# Prédiction IA pour un pays spécifique
@router.post("/predict", response_model=schemas.PredictionOut)
def get_prediction(
    prediction_in: schemas.PredictionIn, # Données d'entrée pour la prédiction, validées par PredictionIn.
    db: Session = Depends(database.get_db), # Injecte une session de base de données.
    current_user: models.User = Depends(auth.get_current_user) # Assure que seul un utilisateur authentifié peut demander une prédiction.
):
    """Effectue une prédiction basée sur les données d'entrée fournies.
    Actuellement, simule une prédiction en doublant le dernier nombre de cas confirmés pour le pays.
    Une implémentation réelle de modèle ML serait intégrée ici."""
    # Pour l'instant, nous renvoyons le dernier nombre de cas confirmés pour le pays spécifié,
    # multiplié par 2 à titre d'exemple simple de prédiction.
    latest_data = db.query(models.Data).filter(models.Data.country == prediction_in.country).order_by(models.Data.date.desc()).first()
    
    if latest_data:
        predicted_value = float(latest_data.confirmed * 2) # Exemple de prédiction simple : double les cas confirmés.
        return {"prediction": predicted_value, "score": 0.8} # Retourne la valeur prédite et un score (exemple).
    else:
        # Lève une exception HTTP 404 si aucune donnée n'est trouvée pour le pays spécifié.
        raise HTTPException(status_code=404, detail=f"No data found for {prediction_in.country} to make a prediction.") 