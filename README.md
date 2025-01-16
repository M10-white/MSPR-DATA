# MSPR-DATA

## Description
Ce projet vise à développer une plateforme pour la collecte, le nettoyage, l'analyse, et la visualisation de données historiques sur les pandémies. L'application permettra aux chercheurs et aux décideurs de consulter des tableaux de bord interactifs et de modéliser des données pour formuler des hypothèses prédictives.

## Table of Contents
[Features](#features)\
[Technologies](#technologies)\
[Architecture](#architecture)\
[Installation](#installation)\
[Usage](#usage)\
[Contributors](#contributors)

## Features
- Collecte de données à partir de fichiers JSON et CSV.
- Nettoyage et tri des données avec gestion des doublons.
- API REST pour manipuler les données (lecture, ajout, modification, suppression).
- Tableaux de bord interactifs pour visualiser des indicateurs clés.
- Documentation complète (modèles de données, API, processus de nettoyage).

## Technologies
### Backend
  Python (Flask/FastAPI)\
  MySQL\
  Pandas (pour le nettoyage des données)

### Frontend
  HTML5\
  CSS/SCSS\
  JavaScript (avec librairies comme D3.js ou Chart.js pour les visualisations)

### Outils de Documentation
  Draw.io (modélisation des données)\
  Swagger (documentation API)\
  Figma (maquettes UI/UX)

### Gestion de Projet
  GitHub (versioning)\
  GanttProject (planification)\
  Méthodologie Agile

## Architecture
```bash
MSPR-DATA/ 
├── backend/ 
│ ├── app/ 
│ ├── migrations/ 
│ └── tests/ 
├── frontend/ 
│ ├── public/ 
│ ├── components/ 
│ └── tests/ 
├── docs/ 
│ ├── database/ 
│ ├── api/ 
│ ├── ui-ux/ 
│ └── project/ 
├── .gitignore 
├── README.md 
└── requirements.txt
```

## Installation
### Prérequis
- Python 3.10 ou supérieur
- MySQL
- Node.js (pour gérer les dépendances SCSS ou JavaScript si nécessaire)

### Étapes
1. Clonez le dépôt :
```bash
git clone https://github.com/username/project-name.git
```

2. Accédez au répertoire backend et installez les dépendances Python :
```bash
cd backend
```
```bash
pip install -r requirements.txt
```

3. Configurez la base de données MySQL :

- Importez le fichier schema.sql situé dans docs/database/.

4. Lancez l'application backend :
```bash
python app/main.py
```

5. Lancer un serveur local pour accéder au projet
Avant tout cela verifiez que vous avez Node.js d'installer.
```bash
node -v
```
Ensuite installez http-server.
```bash
npm install -g http-server
```
Puis lancez le server local.
```bash
cd .\frontend\public\ 
```
```bash
http-server -p 8000
```

### Usage
- Accédez à l'application backend sur http://localhost:5000 (par défaut).
- Consultez les tableaux de bord via le frontend (accédez à index.html dans votre navigateur).

### Contributors
Anas Kotoub : Backend\
Iliana Benchikh : Backend\
Brahim Chaouki : Frontend\
Akram Mahboubi : Frontend
