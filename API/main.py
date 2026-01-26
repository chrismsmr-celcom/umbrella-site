from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from pdf2docx import Converter
from pdf2image import convert_from_path
import os
import tempfile
import shutil
import zipfile

app = FastAPI(title="Umbrella PDF Converter")

# =========================
# ACCUEIL
# =========================
@app.get("/")
def root():
    return {"status": "PDF Converter backend running"}

# -----------------------------
# PDF -> Word (Route corrigée)
# -----------------------------
def convert_pdf_to_word(pdf_path: str, docx_path: str):
    cv = Converter(pdf_path)
    cv.convert(docx_path, start=0, end=None)
    cv.close()
    return docx_path

@app.post("/pdf2word")  # Changé de /convert/pdf-to-word à /pdf2word
async def pdf_to_word(files: list[UploadFile] = File(...)):
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "converted_word_files.zip")
    tasks = []

    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            continue
        pdf_path = os.path.join(temp_dir, file.filename)
        docx_path = pdf_path.replace(".pdf", ".docx")
        with open(pdf_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        tasks.append((pdf_path, docx_path))

    converted_files = []
    for pdf_path, docx_path in tasks:
        converted_files.append(convert_pdf_to_word(pdf_path, docx_path))

    # Zip les fichiers Word
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for docx_file in converted_files:
            zipf.write(docx_file, os.path.basename(docx_file))

    return FileResponse(zip_path, filename="converted_word_files.zip", media_type="application/zip")

# -----------------------------
# PDF -> Images (Route corrigée)
# -----------------------------
def convert_pdf_to_images(pdf_path: str, output_folder: str):
    images = convert_from_path(pdf_path)
    paths = []
    for i, img in enumerate(images):
        img_path = os.path.join(output_folder, f"page_{i+1}.png")
        img.save(img_path, "PNG")
        paths.append(img_path)
    return paths

@app.post("/pdf2image")  # Changé de /convert/pdf-to-images à /pdf2image
async def pdf_to_images(files: list[UploadFile] = File(...)):
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "pdf_images.zip")
    tasks = []

    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            continue
        pdf_path = os.path.join(temp_dir, file.filename)
        with open(pdf_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        output_folder = os.path.join(temp_dir, file.filename.replace(".pdf", ""))
        os.makedirs(output_folder, exist_ok=True)
        tasks.append((pdf_path, output_folder))

    converted_folders = []
    for pdf_path, folder in tasks:
        converted_folders.append((folder, convert_pdf_to_images(pdf_path, folder)))

    # Zip les images
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for folder, imgs in converted_folders:
            for img_file in imgs:
                zipf.write(img_file, os.path.join(os.path.basename(folder), os.path.basename(img_file)))

    return FileResponse(zip_path, filename="pdf_images.zip", media_type="application/zip")

