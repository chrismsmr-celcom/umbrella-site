FROM python:3.10-slim

# Configuration environnement
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

# Installation des dépendances système critiques
RUN apt-get update && apt-get install -y --no-install-recommends \
    # --- Moteur OCR ---
    tesseract-ocr \
    tesseract-ocr-fra \
    tesseract-ocr-eng \
    # --- LibreOffice & Moteur de Rendu (headless) ---
    libreoffice-nogui \
    libreoffice-writer \
    libreoffice-calc \
    libreoffice-java-common \
    openjdk-17-jre-headless \
    # --- Dépendances graphiques critiques pour LibreOffice (même sans UI) ---
    libxinerama1 \
    libdbus-glib-1-2 \
    libcups2 \
    libglu1-mesa \
    # --- Manipulation PDF, Image & Tableaux ---
    ghostscript \
    poppler-utils \
    libvips-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    # --- Support des polices (Vital pour éviter les carrés à la place du texte) ---
    fonts-liberation \
    fonts-dejavu \
    fontconfig \
    # --- Outils de build ---
    gcc \
    python3-dev \
    libsm6 libxext6 libxrender-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Fix pour s'assurer que l'appel 'libreoffice' pointe au bon endroit
RUN ln -s /usr/bin/libreoffice /usr/bin/soffice || true

# Autoriser Ghostscript
RUN sed -i 's/rights="none" pattern="PDF"/rights="read|write" pattern="PDF"/' /etc/ImageMagick-6/policy.xml || true

ENV HOME=/tmp
WORKDIR /app

# Installation Python
COPY requirements.txt .
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 10000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000", "--timeout-keep-alive", "75"]
