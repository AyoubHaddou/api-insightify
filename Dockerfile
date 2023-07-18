# Utiliser une image de base Python
FROM python:3.9

# Définition du répertoire de travail dans le conteneur
WORKDIR /app

# Copie des fichiers de code source dans le conteneur
COPY . /app

# Installation des dépendances
RUN pip install -r requirements.txt

# Exposition du port utilisé par l'API (ajustez si nécessaire)
EXPOSE 8000

# Commande pour lancer l'API FastAPI
CMD ["gunicorn", "main:app"]