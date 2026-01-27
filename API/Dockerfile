FROM python:3.10-slim

# Installation de LibreOffice, Java (pour Camelot), Ghostscript et Poppler
RUN apt-get update && apt-get install -y \
    libreoffice \
    libreoffice-java-common \
    ghostscript \
    python3-tk \
    poppler-utils \
    libgl1-mesa-glx \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Port Render
EXPOSE 10000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
