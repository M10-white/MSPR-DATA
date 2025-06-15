from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
import models
import schemas
import database
from sqlalchemy.orm import Session
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Security configuration
SECRET_KEY = "secret-key-change-me"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme (tokenUrl doit correspondre à la route de login dans FastAPI)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

def verify_password(plain_password, hashed_password):
    """Vérifie si un mot de passe en clair correspond à un mot de passe haché."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Hache un mot de passe en clair."""
    return pwd_context.hash(password)

def get_user(db: Session, username: str):
    """Récupère un utilisateur de la base de données par son nom d'utilisateur."""
    return db.query(models.User).filter(models.User.username == username).first()

def authenticate_user(db: Session, username: str, password: str):
    """Authentifie un utilisateur en vérifiant son nom d'utilisateur et son mot de passe.
    Retourne l'objet utilisateur si l'authentification réussit, False sinon."""
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crée un jeton d'accès JWT avec les données fournies et une date d'expiration."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15) # Expiration par défaut si non spécifiée.
    to_encode.update({"exp": expire}) # Ajoute la date d'expiration au payload du jeton.
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) # Encode le JWT.
    return encoded_jwt

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    """Endpoint pour la connexion des utilisateurs et la génération d'un jeton d'accès JWT."""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        # Lève une exception HTTP 401 si l'authentification échoue.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Calcule la durée d'expiration du jeton.
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # Crée le jeton d'accès avec le nom d'utilisateur comme sujet (sub).
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    # Retourne le jeton d'accès et son type (bearer).
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    """Récupère et valide l'utilisateur courant à partir du jeton d'authentification fourni."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        logger.debug(f"Received token: {token}") # Log le jeton reçu (à des fins de débogage).
        # Décode le jeton JWT en utilisant la clé secrète et l'algorithme spécifié.
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub") # Extrait le nom d'utilisateur du payload.
        if username is None:
            logger.error("Username is None in token payload") # Log l'erreur si le nom d'utilisateur est absent.
            raise credentials_exception
        logger.debug(f"Decoded username from token: {username}") # Log le nom d'utilisateur décodé.
    except JWTError as e:
        logger.error(f"JWT decode error: {str(e)}") # Log les erreurs de décodage JWT.
        raise credentials_exception
    
    # Tente de récupérer l'utilisateur de la base de données en utilisant le nom d'utilisateur extrait.
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        logger.error(f"User not found for username: {username}") # Log l'erreur si l'utilisateur n'est pas trouvé.
        raise credentials_exception
    logger.debug(f"Found user: {user.username}") # Log l'utilisateur trouvé.
    return user # Retourne l'objet utilisateur. 