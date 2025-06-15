# 🌍 MSPR - Système de Prédiction et Analyse des Données COVID-19

## 📝 Description
MSPR est une application web sophistiquée permettant l'analyse et la prédiction des données COVID-19 à travers différents pays. L'application combine une interface utilisateur moderne avec des fonctionnalités d'analyse de données avancées et des prédictions basées sur l'intelligence artificielle.

## ✨ Fonctionnalités Principales

### 📊 Analyse de Données
- Visualisation interactive des données COVID-19
- Graphiques dynamiques montrant l'évolution des cas
- Métriques clés (cas confirmés, décès, guérisons)
- Taux de mortalité et de guérison
- Analyse par pays avec respect des règles RGPD

### 🤖 Prédictions IA
- Prédiction du nombre de cas futurs
- Modèle d'apprentissage automatique entraîné sur les données historiques
- Interface intuitive pour la sélection des paramètres de prédiction
- Score de confiance pour chaque prédiction

### 🔐 Système d'Authentification
- Inscription et connexion sécurisées
- Gestion des sessions utilisateur
- Protection des routes sensibles
- Gestion des droits d'accès

## 🛠️ Technologies Utilisées

### Backend
- **FastAPI** : Framework web moderne et performant
- **SQLAlchemy** : ORM pour la gestion de la base de données
- **Pydantic** : Validation des données
- **JWT** : Authentification sécurisée
- **SQLite** : Base de données légère et portable

### Frontend
- **Streamlit** : Interface utilisateur interactive
- **Plotly** : Visualisations de données avancées
- **Pandas** : Manipulation et analyse des données

## 🚀 Installation

1. **Cloner le Repository**
   ```bash
   git clone [URL_DU_REPO]
   cd MSPR
   ```

2. **Créer un Environnement Virtuel**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   .\venv\Scripts\activate  # Windows
   ```

3. **Installer les Dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialiser la Base de Données**
   ```bash
   python backend/import_csv.py
   ```

## 💻 Utilisation

1. **Démarrer le Backend**
   ```bash
   cd backend
   uvicorn main:app --reload --port 8001
   ```

2. **Démarrer le Frontend**
   ```bash
   cd frontend
   streamlit run app.py
   ```

3. **Accéder à l'Application**
   - Frontend : http://localhost:8501
   - API Documentation : http://localhost:8001/docs

## 📁 Structure du Projet
```
MSPR/
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── routes.py
│   ├── auth.py
│   ├── database.py
│   └── import_csv.py
├── frontend/
│   ├── app.py
│   └── auth.py
├── requirements.txt
└── README.md
```

## 🔒 Sécurité
- Authentification JWT
- Hachage des mots de passe avec bcrypt
- Validation des données avec Pydantic
- Protection contre les injections SQL
- Respect des règles RGPD pour la gestion des données

## 📈 Fonctionnalités d'Analyse
- Visualisation des tendances
- Calcul des taux de mortalité et de guérison
- Analyse comparative entre pays
- Export des données
- Prédictions basées sur l'IA

## 🤝 Contribution
Les contributions sont les bienvenues ! N'hésitez pas à :
1. Fork le projet
2. Créer une branche pour votre fonctionnalité
3. Commiter vos changements
4. Pousser vers la branche
5. Ouvrir une Pull Request

## 📝 Licence
Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 👥 Auteurs
- [Votre Nom] - Développeur Principal

## 🙏 Remerciements
- [Liste des contributeurs]
- [Bibliothèques utilisées]
- [Sources de données]

## 🐳 Déploiement avec Docker

### Prérequis
- Docker
- Docker Compose

### Déploiement Rapide
1. **Cloner le Repository**
   ```bash
   git clone [URL_DU_REPO]
   cd MSPR
   ```

2. **Construire et Démarrer les Conteneurs**
   ```bash
   docker-compose up --build
   ```

3. **Accéder à l'Application**
   - Frontend : http://localhost:8502
   - API Documentation : http://localhost:8001/docs

### Structure Docker
- **Backend** : Service FastAPI exposé sur le port 8001
- **Frontend** : Service Streamlit exposé sur le port 8501
- **Base de données** : SQLite persistante via volume Docker
- **Réseau** : Communication inter-services via réseau Docker

### Commandes Docker Utiles
```bash
# Démarrer les services
docker-compose up

# Démarrer en mode détaché
docker-compose up -d

# Arrêter les services
docker-compose down

# Voir les logs
docker-compose logs -f

# Reconstruire les images
docker-compose build
``` 