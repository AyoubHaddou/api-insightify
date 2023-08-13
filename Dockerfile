# Utiliser une image de base Python
FROM python:3.9-slim

# Définition du répertoire de travail dans le conteneur
WORKDIR /app

# Copie des fichiers de code source dans le conteneur
COPY requirements.txt .

# Installation des dépendances
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

RUN python create_db.py

# Exposition du port utilisé par l'API (ajustez si nécessaire)
EXPOSE 80

RUN pytest

# Commande pour lancer l'API FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--proxy-headers"]