# Utilise une image Python stable
FROM python:3.10-slim

# Install les dépendances système (Poppler pour les images et Mesa pour pdf2docx)
RUN apt-get update && apt-get install -y \
    poppler-utils \
    libgl1-mesa-glx \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Définit le dossier de travail
WORKDIR /app

# Copie le fichier des dépendances
COPY requirements.txt .

# Installe les bibliothèques Python
RUN pip install --no-cache-dir -r requirements.txt

# Copie tout le reste du code
COPY . .

# Expose le port utilisé par Render (10000 par défaut)
EXPOSE 10000

# Commande pour lancer l'application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
