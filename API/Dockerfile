FROM python:3.10-slim

# 1. Configuration des variables d'environnement critiques
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    # LibreOffice écrit souvent dans $HOME, on le force sur /tmp (seul dossier inscriptible sur Render)
    HOME=/tmp \
    JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

WORKDIR /app

# 2. Installation groupée pour réduire le nombre de couches et la taille
RUN apt-get update && apt-get install -y --no-install-recommends \
    # --- Moteur OCR (Léger) ---
    tesseract-ocr \
    tesseract-ocr-fra \
    # --- LibreOffice Headless (Version minimale sans GUI) ---
    libreoffice-nogui \
    libreoffice-writer \
    libreoffice-calc \
    openjdk-17-jre-headless \
    # --- Dépendances de rendu graphique (Essentiels pour éviter les crashes) ---
    libxinerama1 libdbus-glib-1-2 libcups2 libglu1-mesa libsm6 libxrender1 libfontconfig1 \
    # --- Utilitaires PDF & Image ---
    ghostscript poppler-utils \
    # --- Polices de caractères (Évite les carrés/disparition de texte) ---
    fonts-liberation fonts-dejavu \
    # --- Outils de build temporaires ---
    gcc python3-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 3. Sécurité Ghostscript (nécessaire pour la manipulation PDF sécurisée)
RUN sed -i 's/rights="none" pattern="PDF"/rights="read|write" pattern="PDF"/' /etc/ImageMagick-6/policy.xml || true

# 4. Installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

# 5. Copie du code
COPY . .

# 6. Configuration des permissions (Render tourne souvent en mode non-root)
RUN chmod -R 777 /tmp

# 7. Port par défaut Render
EXPOSE 10000

# 8. Commande de lancement optimisée pour la stabilité
# On limite les workers à 1 ou 2 si tu as moins de 2Go de RAM pour éviter le crash (OOM)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000", "--workers", "1", "--timeout-keep-alive", "75"]
