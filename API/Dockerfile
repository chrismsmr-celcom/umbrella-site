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
    # --- Conversion Office (Word, PPT, Excel) ---
    libreoffice \
    libreoffice-java-common \
    # --- Manipulation PDF & Image ---
    ghostscript \
    poppler-utils \
    libvips-dev \
    libgl1-mesa-glx \
    # --- Support des polices pour le rendu PDF ---
    fonts-liberation \
    fontconfig \
    # --- Outils de build ---
    gcc \
    python3-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Gestion des polices (Indispensable pour "Add Watermark" ou "Add page numbers")
RUN fc-cache -f -v

# Installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY . .

# Port Render
EXPOSE 10000

# Lancement avec Uvicorn
# On utilise un worker unique pour économiser la RAM sur Render à cause de LibreOffice
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000", "--workers", "1"]
