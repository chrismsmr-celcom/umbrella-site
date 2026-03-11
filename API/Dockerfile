FROM python:3.10-slim

# Éviter les fichiers .pyc et activer le mode non-interactif
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Installation des dépendances système
# Ajout de tesseract-ocr-eng pour la compatibilité avec tes documents d'assurance
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-fra \
    tesseract-ocr-eng \
    libreoffice \
    libreoffice-java-common \
    ghostscript \
    python3-tk \
    poppler-utils \
    libgl1-mesa-glx \
    fonts-liberation \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Optimisation du cache Docker pour les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY . .

# Port pour Render (Utilisation de la variable d'environnement PORT si nécessaire)
EXPOSE 10000

# Lancement avec Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
