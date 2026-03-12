import requests
import os
import time
from contextlib import ExitStack

# ========================
# CONFIGURATION
# ========================
# Vérifie que l'URL ne finit pas par un slash
BASE_URL = "https://umbrella-site-1pdf-covert.onrender.com"

# ========================
# UTILITAIRES DE GESTION DE FICHIERS
# ========================
def send_request(endpoint, files, data=None, output_name="result.zip"):
    url = f"{BASE_URL}/{endpoint}"
    start_time = time.time()
    
    try:
        print(f"🚀 [Umbrella Engine] Opération : {endpoint}...")
        # Augmentation du timeout à 300s car LibreOffice/OCR sur Render peut être lent
        response = requests.post(url, files=files, data=data, timeout=300)
        
        duration = round(time.time() - start_time, 2)

        if response.status_code == 200:
            # CORRECTION INDENTATION ICI
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
        print("❌ Erreur : Le serveur a mis trop de temps (Timeout).")
    except Exception as e:
        print(f"❌ Erreur de connexion : {e}")

# ========================
# FONCTIONS ORGANIZE
# ========================

def umbrella_merge(pdf_paths, output_name="merged_umbrella.pdf"):
    with ExitStack() as stack:
        # Clé 'files' (pluriel) comme défini dans ton API merge
        files = [
            ("files", (os.path.basename(p), stack.enter_context(open(p, "rb")), "application/pdf")) 
            for p in pdf_paths if os.path.exists(p)
        ]
        if not files: return
        send_request("organize/merge", files, output_name=output_name)

def umbrella_split(pdf_path, output_name="split_pages.zip"):
    if not os.path.exists(pdf_path): return
    with open(pdf_path, "rb") as f:
        # Clé 'file' (singulier) comme défini dans ton API split
        files = [("file", (os.path.basename(pdf_path), f, "application/pdf"))]
        send_request("organize/split", files, output_name=output_name)

# ========================
# FONCTIONS CONVERT
# ========================

def umbrella_pdf_to_word(pdf_paths, output_name="converted_word.zip"):
    with ExitStack() as stack:
        files = [
            ("files", (os.path.basename(p), stack.enter_context(open(p, "rb")), "application/pdf")) 
            for p in pdf_paths if os.path.exists(p)
        ]
        send_request("convert/pdf-to-word", files, output_name=output_name)

def umbrella_office_to_pdf(doc_paths, output_name="converted_office.zip"):
    with ExitStack() as stack:
        files = [
            ("files", (os.path.basename(p), stack.enter_context(open(p, "rb")), "application/octet-stream")) 
            for p in doc_paths if os.path.exists(p)
        ]
        send_request("convert/office-to-pdf", files, output_name=output_name)

def umbrella_pdf_to_jpg(pdf_path, output_name="pdf_pages_images.zip"):
    if not os.path.exists(pdf_path): return
    with open(pdf_path, "rb") as f:
        # Clé 'file' (singulier) pour l'endpoint jpg
        files = [("file", (os.path.basename(pdf_path), f, "application/pdf"))]
        send_request("convert/pdf-to-jpg", files, output_name=output_name)

# ========================
# FONCTION SECURITY
# ========================

def umbrella_protect(pdf_path, password, output_name="protected_doc.pdf"):
    if not os.path.exists(pdf_path): return
    with open(pdf_path, "rb") as f:
        # Clé 'file' (singulier)
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
