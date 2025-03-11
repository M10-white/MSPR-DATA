#!/bin/bash

echo "🚀 Vérification et installation des dépendances Python..."
pip install -r requirements.txt

echo "🚀 Vérification de PostgreSQL..."
pg_isready -h localhost -p 5432 -U postgres
if [ $? -ne 0 ]; then
    echo "❌ PostgreSQL n'est pas accessible. Assurez-vous qu'il est démarré."
    exit 1
fi

echo "🔍 Vérification et création des tables dans PostgreSQL..."
python backend/etl_pipeline.py

echo "🚀 Démarrage de l'API FastAPI..."
uvicorn backend.fastapi_postgres_api:app --reload &

API_PID=$!

echo "🚀 Démarrage du serveur frontend..."
cd frontend/public
http-server -p 8000 &

FRONTEND_PID=$!

echo "✅ Tout est en cours d'exécution ! 🎉"
echo "ℹ️ API disponible sur http://127.0.0.1:8000"
echo "ℹ️ Frontend disponible sur http://127.0.0.1:8000"

# Attendre la fin des processus
wait $API_PID
wait $FRONTEND_PID
