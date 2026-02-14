 import requests

# ========================
# CONFIG
# ========================
BASE_URL = "https://umbrella-site-qr-code.onrender.com"

# ========================
# PDF → Word
# ========================
def pdf_to_word(pdf_paths):
    url = f"{BASE_URL}/convert/pdf-to-word"
    files = [("files", (pdf, open(pdf, "rb"), "application/pdf")) for pdf in pdf_paths]

    response = requests.post(url, files=files)
    if response.status_code == 200:
        output_file = "converted_word_files.zip"
        with open(output_file, "wb") as f:
            f.write(response.content)
        print(f"✅ PDF → Word terminé : {output_file}")
    else:
        print("❌ Erreur PDF → Word :", response.text)

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
