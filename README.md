# MSPR-DATA

## Description
Ce projet vise à développer une plateforme pour la collecte, le nettoyage, l'analyse, et la visualisation de données historiques sur les pandémies. L'application permettra aux chercheurs et aux décideurs de consulter des tableaux de bord interactifs et de modéliser des données pour formuler des hypothèses prédictives.

## Table of Contents
[Features](#features)  
[Technologies](#technologies)  
[Architecture](#architecture)  
[Installation](#installation)  
[Usage](#usage)  
[Contributors](#contributors)  

## Features
- Collecte de données à partir de fichiers JSON et CSV.
- Nettoyage et tri des données avec gestion des doublons.
- API REST pour manipuler les données (lecture, ajout, modification, suppression).
- Tableaux de bord interactifs pour visualiser des indicateurs clés.
- Documentation complète (modèles de données, API, processus de nettoyage).

## Technologies
### Backend
- **Python** (FastAPI, Prefect, Pandas)
- **PostgreSQL** (Base de données relationnelle)
- **Uvicorn** (Serveur ASGI pour FastAPI)

### Frontend
- **HTML5**, **CSS/SCSS**
- **JavaScript**

### Outils de Documentation
- **Draw.io** (Modélisation des données)
- **Swagger** (Documentation API)
- **Figma** (Maquettes UI/UX)

### Gestion de Projet
- **GitHub** (Versioning)
- **Méthodologie Agile**

## Architecture
```bash
MSPR-DATA/ 
├── backend/ 
│   ├── etl_pipeline.py
│   ├── fastapi_postgres_api.py
│   ├── models.py
│   └── tests/ 
├── frontend/ 
│   ├── public/ 
│   ├── components/ 
│   └── tests/ 
├── docs/ 
│   ├── database/ 
│   ├── api/ 
│   ├── ui-ux/ 
│   └── project/ 
├── start.sh
├── .gitignore 
├── README.md 
└── requirements.txt
```

## Installation
### Prérequis
- **Python 3.10+**
- **PostgreSQL installé et démarré**
- **Node.js installé pour le serveur frontend**

### Installation de PostgreSQL
Si PostgreSQL n'est pas installé, suivez ces étapes :

#### Windows
1. **Téléchargez l'installateur** depuis [https://www.postgresql.org/download/](https://www.postgresql.org/download/).
2. **Lancez l'installation** et suivez les instructions.
3. **Notez le mot de passe de l'utilisateur `postgres`**.
4. **Ajoutez PostgreSQL au PATH** (option activée par défaut dans l'installateur).

#### Linux (Debian/Ubuntu)
```bash
sudo apt update && sudo apt install postgresql postgresql-contrib -y
```
#### macOS (via Homebrew)
```bash
brew install postgresql
```

### Ajouter PostgreSQL au PATH sous Windows
1. **Ouvrez l'explorateur de fichiers** et allez dans :  
   ```
   C:\Program Files\PostgreSQL\
   ```
2. **Allez dans le dossier de votre version (`15` ou autre).**
3. **Entrez dans le dossier `bin` et copiez ce chemin**, par exemple :
   ```
   C:\Program Files\PostgreSQL\15\bin
   ```
4. **Ajoutez ce chemin au PATH** :
   - **Ouvrez les paramètres Windows** → Tapez **"Variables d'environnement"**.
   - Dans **Variables système**, sélectionnez `Path` → **Modifier**.
   - **Ajoutez un nouveau chemin** et collez celui copié.
   - **Validez avec OK**.

5. **Redémarrez votre terminal** et testez avec :
   ```bash
   pg_isready -h localhost -p 5432 -U postgres
   ```

### Étapes
1. **Placez-vous dans le bon répertoire** où vous souhaitez cloner le projet :
```bash
cd /chemin/vers/votre/dossier
```

2. **Clonez le dépôt** :
```bash
git clone https://github.com/M10-white/MSPR-DATA.git
cd MSPR-DATA
```

3. **Installez les dépendances** :
```bash
pip install -r requirements.txt
```

4. **Vérifiez et démarrez PostgreSQL** :
```bash
pg_isready -h localhost -p 5432 -U postgres
```
Si PostgreSQL n'est pas actif, démarrez-le via votre gestionnaire de services ou avec :
```bash
sudo systemctl start postgresql
```

5. **Lancez le pipeline ETL, l'API et le frontend** :
```bash
chmod +x start.sh  # Autoriser l'exécution du script
./start.sh  # Exécuter le script
```

6. **Tester si tout fonctionne** :
#### 🌐 **Vérifier l'API**
- Accédez à l'interface Swagger :  
  👉 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Vérifiez l’état de la connexion à PostgreSQL :
  👉 [http://127.0.0.1:8000/test_connection/](http://127.0.0.1:8000/test_connection/)

#### 🖥️ **Accéder au site**
Ouvrez **[http://127.0.0.1:8000](http://127.0.0.1:8000)** dans votre navigateur.

---

## 🛠 **Dépannage**
### **PostgreSQL ne démarre pas ?**
```bash
sudo systemctl start postgresql
```
### **Erreur `ForeignKeyViolation` dans `etl_pipeline.py` ?**
Ajoutez un utilisateur dans PostgreSQL :
```sql
INSERT INTO users (username, email, password) VALUES ('admin', 'admin@email.com', 'password123');
```
Puis relancez :
```bash
python backend/etl_pipeline.py
```

### **Erreur `Address already in use` sur le port 8000 ?**
Trouvez le processus en cours :
```bash
lsof -i :8000
```
Puis tuez-le :
```bash
kill -9 <PID>
```

---

## Contributors
- **Anas Kotoub** : Backend
- **Iliana Benchikh** : Backend
- **Brahim Chaouki** : Frontend & Backend
- **Akram Mahboubi** : Frontend

