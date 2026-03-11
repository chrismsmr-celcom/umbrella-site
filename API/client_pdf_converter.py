import requests
import os

# ========================
# CONFIGURATION
# ========================
# Ton URL de déploiement sur Render
BASE_URL = "https://umbrella-site-qr-code.onrender.com"

# ========================
# FONCTION PDF → WORD
# ========================
def pdf_to_word(pdf_paths):
    """Envoie des PDF au moteur Umbrella pour conversion Word (avec OCR auto)"""
    url = f"{BASE_URL}/convert/pdf-to-word"
    
    files = []
    opened_files = []
    
    try:
        for pdf in pdf_paths:
            if os.path.exists(pdf):
                f = open(pdf, "rb")
                opened_files.append(f)
                files.append(("files", (os.path.basename(pdf), f, "application/pdf")))
        
        if not files:
            print("⚠️ Aucun fichier valide trouvé.")
            return

        print(f"🚀 Envoi de {len(files)} fichier(s) vers Umbrella Engine...")
        response = requests.post(url, files=files)
        
        if response.status_code == 200:
            output_zip = "umbrella_word_results.zip"
            with open(output_zip, "wb") as out:
                out.write(response.content)
            print(f"✅ Conversion terminée ! Fichiers sauvegardés dans : {output_zip}")
        else:
            print(f"❌ Erreur Serveur ({response.status_code}) : {response.text}")
            
    finally:
        # Toujours fermer les fichiers ouverts
        for f in opened_files:
            f.close()

# ========================
# FONCTION PDF → IMAGES
# ========================
def pdf_to_images(pdf_paths):
    """Envoie des PDF pour extraction d'images"""
    url = f"{BASE_URL}/convert/pdf-to-images"
    files = [("files", (os.path.basename(p), open(p, "rb"), "application/pdf")) for p in pdf_paths if os.path.exists(p)]

    if not files: return

    response = requests.post(url, files=files)
    if response.status_code == 200:
        output_zip = "umbrella_images.zip"
        with open(output_zip, "wb") as f:
            f.write(response.content)
        print(f"✅ PDF → Images terminé : {output_zip}")
    else:
        print("❌ Erreur PDF → Images :", response.text)

# ========================
# ZONE DE TEST
# ========================
if __name__ == "__main__":
    # Liste de tes fichiers locaux à tester (ex: ta police d'assurance)
    # Assure-toi que ces fichiers sont dans le même dossier que ce script
    mes_fichiers = ["insurance_policy.pdf"] 

    print("--- DÉMARRAGE DES TESTS UMBRELLA ENGINE ---")
    
    # Test de la conversion Word (qui déclenchera l'OCR sur le serveur si besoin)
    pdf_to_word(mes_fichiers)

    # Test de l'extraction d'images
    # pdf_to_images(mes_fichiers)
