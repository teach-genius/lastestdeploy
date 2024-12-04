FROM python:3.10-slim

# Installer les dépendances nécessaires pour psycopg2
RUN apt-get update && apt-get install -y gcc libpq-dev && apt-get clean
COPY static /app/static

# Installer les dépendances Python
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
RUN pip install huggingface_hub
# Copier tout le reste du projet
WORKDIR /app
COPY . .

# Exposer le port de l'API
EXPOSE 8000

# Commande pour démarrer l'application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

