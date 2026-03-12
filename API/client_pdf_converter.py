import requests
import os
import time
from contextlib import ExitStack

# ========================
# CONFIGURATION
# ========================
BASE_URL = "https://umbrella-site-qr-code.onrender.com"

# ========================
# UTILITAIRES DE GESTION DE FICHIERS
# ========================
def send_request(endpoint, files, data=None, output_name="result.zip"):
    """
    Fonction générique robuste pour communiquer avec l'API Umbrella.
    Gère les erreurs de timeout et affiche des détails sur les échecs.
    """
    url = f"{BASE_URL}/{endpoint}"
    start_time = time.time()
    
    try:
        print(f"🚀 [Umbrella Engine] Opération : {endpoint}...")
        # Timeout de 120s car l'OCR ou LibreOffice peut être long sur Render
        response = requests.post(url, files=files, data=data, timeout=120)
        
        duration = round(time.time() - start_time, 2)

        if response.status_code == 200:
           with open(output_name, "wb") as out:
    for chunk in response.iter_content(chunk_size=8192):
        out.write(chunk)
            print(f"✅ Succès ({duration}s) ! Fichier sauvegardé : {output_name}")
        else:
            print(f"❌ Erreur Serveur ({response.status_code}) après {duration}s")
            try:
                print(f"   Détails : {response.json().get('detail', response.text)}")
            except:
                print(f"   Détails : {response.text[:200]}")
                
    except requests.exceptions.Timeout:
        print("❌ Erreur : Le serveur a mis trop de temps à répondre (Timeout).")
    except Exception as e:
        print(f"❌ Erreur de connexion : {e}")

# ========================
# FONCTIONS ORGANIZE
# ========================

def umbrella_merge(pdf_paths, output_name="merged_umbrella.pdf"):
    """Fusionne plusieurs PDF en un seul (Clé: 'files')"""
    with ExitStack() as stack:
        opened_files = [stack.enter_context(open(p, "rb")) for p in pdf_paths if os.path.exists(p)]
        if not opened_files:
            print("⚠️ Aucun fichier valide trouvé pour la fusion.")
            return
        
        files = [("files", (os.path.basename(f.name), f, "application/pdf")) for f in opened_files]
        send_request("organize/merge", files, output_name=output_name)

def umbrella_split(pdf_path, output_name="split_pages.zip"):
    """Sépare chaque page d'un PDF (Clé: 'file')"""
    if not os.path.exists(pdf_path): return
    with open(pdf_path, "rb") as f:
        files = [("file", (os.path.basename(pdf_path), f, "application/pdf"))]
        send_request("organize/split", files, output_name=output_name)

# ========================
# FONCTIONS CONVERT
# ========================

def umbrella_pdf_to_word(pdf_paths, output_name="converted_word.zip"):
    """Conversion PDF -> Word avec OCR auto (Clé: 'files')"""
    with ExitStack() as stack:
        opened_files = [stack.enter_context(open(p, "rb")) for p in pdf_paths if os.path.exists(p)]
        if not opened_files: return
        
        files = [("files", (os.path.basename(f.name), f, "application/pdf")) for f in opened_files]
        send_request("convert/pdf-to-word", files, output_name=output_name)

def umbrella_office_to_pdf(doc_paths, output_name="converted_office.zip"):
    """Word/Excel/PPT -> PDF via LibreOffice (Clé: 'files')"""
    with ExitStack() as stack:
        opened_files = [stack.enter_context(open(p, "rb")) for p in doc_paths if os.path.exists(p)]
        if not opened_files: return
        
        files = [("files", (os.path.basename(f.name), f, "application/octet-stream")) for f in opened_files]
        send_request("convert/office-to-pdf", files, output_name=output_name)

def umbrella_pdf_to_jpg(pdf_path, output_name="pdf_pages_images.zip"):
    """Convertit un PDF en images JPG (Clé: 'file')"""
    if not os.path.exists(pdf_path): return
    with open(pdf_path, "rb") as f:
        files = [("file", (os.path.basename(pdf_path), f, "application/pdf"))]
        send_request("convert/pdf-to-jpg", files, output_name=output_name)

def umbrella_images_to_pdf(image_paths, output_name="images_combined.pdf"):
    """Combine plusieurs images en un PDF (Clé: 'files')"""
    with ExitStack() as stack:
        opened_files = [stack.enter_context(open(p, "rb")) for p in image_paths if os.path.exists(p)]
        if not opened_files: return
        
        files = [("files", (os.path.basename(f.name), f, "image/jpeg")) for f in opened_files]
        send_request("convert/images-to-pdf", files, output_name=output_name)

# ========================
# FONCTION SECURITY
# ========================

def umbrella_protect(pdf_path, password, output_name="protected_doc.pdf"):
    """Verrouille un PDF avec mot de passe (Clé: 'file')"""
    if not os.path.exists(pdf_path): return
    with open(pdf_path, "rb") as f:
        files = [("file", (os.path.basename(pdf_path), f, "application/pdf"))]
        data = {"password": password}
        send_request("security/protect", files, data=data, output_name=output_name)

# ========================
# ZONE DE TEST (MAIN)
# ========================
if __name__ == "__main__":
    print("\n--- 🛡️ UMBRELLA ENGINE PRO : CLIENT DE TEST ---")
    
    # -- TEST 1 : FUSION --
    # umbrella_merge(["devis.pdf", "contrat.pdf"], "dossier_complet.pdf")
    
    # -- TEST 2 : PDF TO WORD (OCR) --
    # Si tu as une police d'assurance scannée :
    # umbrella_pdf_to_word(["assurance_scan.pdf"], "assurance_editable.zip")
    
    # -- TEST 3 : PDF TO JPG --
    # umbrella_pdf_to_jpg("presentation.pdf", "slides_images.zip")
    
    # -- TEST 4 : OFFICE TO PDF --
    # umbrella_office_to_pdf(["facture.docx", "budget.xlsx"], "archives_pdf.zip")
    
    # -- TEST 5 : PROTECTION --
    # umbrella_protect("confidentiel.pdf", "christopher2026", "confidentiel_locked.pdf")

    print("\n--- FIN DES TESTS ---\n")
