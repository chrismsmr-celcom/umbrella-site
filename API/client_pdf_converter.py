 import requests

# ========================
# CONFIG
# ========================
BASE_URL = "https://umbrella-site-qr-code.onrender.com"

# ========================
# PDF → Word
# ========================
def process_pdf_to_word(pdf_path, docx_path):
    try:
        # 1. Tentative normale avec pdf2docx
        cv = Converter(pdf_path)
        cv.convert(docx_path)
        cv.close()
        
        # 2. Vérification : si le fichier est tout petit (moins de 5ko), c'est probablement un scan
        # Ou si tu veux forcer l'OCR sur les scans, on peut faire une vérification de contenu
        if os.path.getsize(docx_path) < 5000:
            print(f"Détection de scan pour {pdf_path}, passage en mode OCR...")
            doc = Document()
            images = convert_from_path(pdf_path)
            
            for img in images:
                # Extraction du texte (langue française)
                text = pytesseract.image_to_string(img, lang='fra')
                doc.add_paragraph(text)
                doc.add_page_break()
            
            doc.save(docx_path)
            
        return docx_path
    except Exception as e:
        print(f"Erreur conversion: {e}")
        return None
# ========================
# PDF → Images
# ========================
def pdf_to_images(pdf_paths):
    url = f"{BASE_URL}/convert/pdf-to-images"
    files = [("files", (pdf, open(pdf, "rb"), "application/pdf")) for pdf in pdf_paths]

    response = requests.post(url, files=files)
    if response.status_code == 200:
        output_file = "pdf_images.zip"
        with open(output_file, "wb") as f:
            f.write(response.content)
        print(f"✅ PDF → Images terminé : {output_file}")
    else:
        print("❌ Erreur PDF → Images :", response.text)

# ========================
# TEST
# ========================
if __name__ == "__main__":
    # Mettez ici vos fichiers PDF à convertir
    pdf_files = ["test.pdf", "example.pdf"]

    # Conversion PDF → Word
    pdf_to_word(pdf_files)

    # Conversion PDF → Images
    pdf_to_images(pdf_files)
