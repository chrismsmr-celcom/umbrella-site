import requests
import os

# ========================
# CONFIGURATION
# ========================
BASE_URL = "https://umbrella-site-qr-code.onrender.com"

# ========================
# UTILITAIRES DE GESTION DE FICHIERS
# ========================
def send_request(endpoint, files, data=None, output_name="result.zip"):
    """Fonction générique pour envoyer des fichiers à Umbrella"""
    url = f"{BASE_URL}/{endpoint}"
    try:
        print(f"🚀 Opération [{endpoint}] en cours...")
        response = requests.post(url, files=files, data=data)
        
        if response.status_code == 200:
            with open(output_name, "wb") as out:
                out.write(response.content)
            print(f"✅ Succès ! Fichier sauvegardé : {output_name}")
        else:
            print(f"❌ Erreur Serveur ({response.status_code}) : {response.text}")
    except Exception as e:
        print(f"❌ Erreur de connexion : {e}")

# ========================
# FONCTIONS ORGANIZE
# ========================

def umbrella_merge(pdf_paths, output_name="merged_umbrella.pdf"):
    """Fusionne plusieurs PDF en un seul"""
    opened_files = [open(p, "rb") for p in pdf_paths if os.path.exists(p)]
    files = [("files", (os.path.basename(f.name), f, "application/pdf")) for f in opened_files]
    
    if not files: return
    send_request("organize/merge", files, output_name=output_name)
    for f in opened_files: f.close()

def umbrella_split(pdf_path, output_name="split_pages.zip"):
    """Sépare chaque page d'un PDF"""
    if not os.path.exists(pdf_path): return
    with open(pdf_path, "rb") as f:
        files = [("file", (os.path.basename(pdf_path), f, "application/pdf"))]
        send_request("organize/split", files, output_name=output_name)

# ========================
# FONCTIONS CONVERT
# ========================

def umbrella_pdf_to_word(pdf_paths, output_name="converted_word.zip"):
    """Conversion PDF -> Word avec détection OCR auto"""
    opened_files = [open(p, "rb") for p in pdf_paths if os.path.exists(p)]
    files = [("files", (os.path.basename(f.name), f, "application/pdf")) for f in opened_files]
    
    if not files: return
    send_request("convert/pdf-to-word", files, output_name=output_name)
    for f in opened_files: f.close()

def umbrella_office_to_pdf(doc_paths, output_name="converted_from_office.zip"):
    """Conversion Word/Excel/PPT -> PDF (via LibreOffice Headless)"""
    opened_files = [open(p, "rb") for p in doc_paths if os.path.exists(p)]
    # On laisse le serveur gérer le MIME type selon l'extension
    files = [("files", (os.path.basename(f.name), f, "application/octet-stream")) for f in opened_files]
    
    if not files: return
    send_request("convert/office-to-pdf", files, output_name=output_name)
    for f in opened_files: f.close()

# ========================
# FONCTION SECURITY
# ========================

def umbrella_protect(pdf_path, password, output_name="protected_doc.pdf"):
    """Ajoute un mot de passe à un PDF"""
    if not os.path.exists(pdf_path): return
    with open(pdf_path, "rb") as f:
        files = [("file", (os.path.basename(pdf_path), f, "application/pdf"))]
        data = {"password": password}
        send_request("security/protect", files, data=data, output_name=output_name)

# ========================
# ZONE DE TEST (MAIN)
# ========================
if __name__ == "__main__":
    print("--- STARTING UMBRELLA ENGINE CLIENT TEST ---")
    
    # 1. Test Fusion (Merge)
    # umbrella_merge(["doc1.pdf", "doc2.pdf"], "final_fusion.pdf")
    
    # 2. Test Word avec OCR (Idéal pour tes polices d'assurance scannées)
    mes_scans = ["insurance_policy.pdf"]
    umbrella_pdf_to_word(mes_scans, "resultats_ocr.zip")
    
    # 3. Test Protection (Mot de passe)
    # umbrella_protect("secret.pdf", "mon_code_123", "secret_locked.pdf")
    
    # 4. Test Conversion Office
    # umbrella_office_to_pdf(["devis.docx", "data.xlsx"], "archive_pdf.zip")
