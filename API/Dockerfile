FROM python:3.10-slim

# Configuration environnement
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Installation des dépendances système critiques
RUN apt-get update && apt-get install -y --no-install-recommends \
    # --- Moteur OCR ---
    tesseract-ocr \
    tesseract-ocr-fra \
    tesseract-ocr-eng \
    # --- Conversion Office (Version minimale sans UI pour économiser 200MB) ---
    libreoffice-writer \
    libreoffice-calc \
    libreoffice-impress \
    # --- Manipulation PDF, Image & Tableaux (Camelot) ---
    ghostscript \
    poppler-utils \
    libvips-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    # --- Support des polices ---
    fonts-liberation \
    fontconfig \
    # --- Outils de build ---
    gcc \
    python3-dev \
    # Indispensable pour Camelot/OpenCV
    libsm6 libxext6 libxrender-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
# Autoriser Ghostscript à traiter les PDF sans restrictions de sécurité trop strictes
RUN sed -i 's/rights="none" pattern="PDF"/rights="read|write" pattern="PDF"/' /etc/ImageMagick-6/policy.xml || true
ENV HOME=/tmp
WORKDIR /app

# Installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY . .

# Port Render
EXPOSE 10000

# Lancement
# Ajout du paramètre --timeout-keep-alive pour les gros fichiers PDF
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000", "--timeout-keep-alive", "75", "--limit-concurrency", "10"]
