from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pdf2docx import Converter
from pdf2image import convert_from_path
import os
import tempfile
import shutil
import zipfile

app = FastAPI()

# Configuration CORS pour accepter les requêtes du navigateur
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def convert_pdf_to_word(pdf_path, docx_path):
    try:
        cv = Converter(pdf_path)
        cv.convert(docx_path)
        cv.close()
        return docx_path
    except Exception as e:
        print(f"Erreur Word: {e}")
        return None

def convert_pdf_to_images(pdf_path, output_folder):
    try:
        images = convert_from_path(pdf_path)
        paths = []
        for i, img in enumerate(images):
            img_path = os.path.join(output_folder, f"page_{i+1}.png")
            img.save(img_path, "PNG")
            paths.append(img_path)
        return paths
    except Exception as e:
        print(f"Erreur Image: {e}")
        return []

@app.post("/pdf2word")
async def pdf_to_word(files: list[UploadFile] = File(...)):
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "word_files.zip")
    converted = []
    
    for file in files:
        p_path = os.path.join(temp_dir, file.filename)
        d_path = p_path.replace(".pdf", ".docx")
        with open(p_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        if convert_pdf_to_word(p_path, d_path):
            converted.append(d_path)

    if not converted: raise HTTPException(400, "Échec de conversion")
    
    with zipfile.ZipFile(zip_path, "w") as z:
        for f in converted: z.write(f, os.path.basename(f))
    return FileResponse(zip_path, filename="converti_word.zip")

@app.post("/pdf2image")
async def pdf_to_image(files: list[UploadFile] = File(...)):
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "image_files.zip")
    
    with zipfile.ZipFile(zip_path, "w") as z:
        for file in files:
            p_path = os.path.join(temp_dir, file.filename)
            with open(p_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            folder = os.path.join(temp_dir, "imgs")
            os.makedirs(folder, exist_ok=True)
            for img in convert_pdf_to_images(p_path, folder):
                z.write(img, os.path.join(file.filename, os.path.basename(img)))
                
    return FileResponse(zip_path, filename="converti_images.zip")
