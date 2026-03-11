from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pdf2docx import Converter
from pdf2image import convert_from_path
from docx import Document
from typing import List
from concurrent.futures import ThreadPoolExecutor
import tempfile, os, shutil, zipfile, subprocess, pytesseract, camelot
from PIL import Image

app = FastAPI(title="Umbrella PDF Engine PRO")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

LIBREOFFICE_BIN = "soffice"

@app.get("/")
def root():
    return {"status": "Umbrella Engine Online", "environment": "Docker Linux OCR-Ready"}

# --- LOGIQUE PDF -> WORD INTELLIGENTE ---
def process_pdf_to_word(pdf_path, docx_path):
    try:
        # 1. Tentative avec pdf2docx (pour garder mise en page, tableaux et polices)
        cv = Converter(pdf_path)
        cv.convert(docx_path, start=0, end=None)
        cv.close()

        # 2. Détection de scan : Si le Word généré est quasi vide (< 5 Ko)
        if os.path.exists(docx_path) and os.path.getsize(docx_path) < 5000:
            print(f"--- SCAN DÉTECTÉ POUR {os.path.basename(pdf_path)} : PASSAGE OCR ---")
            
            doc = Document()
            # On convertit le PDF en images pour l'OCR
            pages = convert_from_path(pdf_path)
            
            for i, page in enumerate(pages):
                # OCR avec support Français + Anglais
                text = pytesseract.image_to_string(page, lang='fra+eng')
                doc.add_paragraph(text)
                if i < len(pages) - 1:
                    doc.add_page_break()
            
            doc.save(docx_path)
            
        return docx_path
    except Exception as e:
        print(f"Erreur technique sur {pdf_path} : {e}")
        return None

@app.post("/convert/pdf-to-word")
async def pdf_to_word(files: List[UploadFile] = File(...)):
    temp_dir = tempfile.mkdtemp()
    try:
        zip_path = os.path.join(temp_dir, "converted_word_files.zip")
        tasks = []
        
        for file in files:
            p = os.path.join(temp_dir, file.filename)
            d = p.replace(".pdf", ".docx")
            with open(p, "wb") as f:
                shutil.copyfileobj(file.file, f)
            tasks.append((p, d))
        
        # Traitement parallèle pour plus de rapidité
        with ThreadPoolExecutor() as ex:
            results = list(ex.map(lambda t: process_pdf_to_word(*t), tasks))
        
        with zipfile.ZipFile(zip_path, "w") as z:
            for r in [res for res in results if res]:
                z.write(r, os.path.basename(r))
        
        return FileResponse(zip_path, filename="word_converted.zip")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- PDF -> IMAGES ---
@app.post("/convert/pdf-to-images")
async def pdf_to_images(files: List[UploadFile] = File(...)):
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "pdf_images.zip")
    
    with zipfile.ZipFile(zip_path, "w") as z:
        for file in files:
            p = os.path.join(temp_dir, file.filename)
            with open(p, "wb") as f: shutil.copyfileobj(file.file, f)
            imgs = convert_from_path(p)
            for i, img in enumerate(imgs):
                img_name = f"{os.path.splitext(file.filename)[0]}_page_{i+1}.png"
                img_path = os.path.join(temp_dir, img_name)
                img.save(img_path, "PNG")
                z.write(img_path, img_name)
    return FileResponse(zip_path, filename="images.zip")

# --- OFFICE -> PDF (LibreOffice Headless) ---
@app.post("/convert/office-to-pdf")
async def office_to_pdf(files: List[UploadFile] = File(...)):
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "office_to_pdf.zip")
    
    for file in files:
        in_p = os.path.join(temp_dir, file.filename)
        with open(in_p, "wb") as f: shutil.copyfileobj(file.file, f)
        subprocess.run([LIBREOFFICE_BIN, "--headless", "--convert-to", "pdf", in_p, "--outdir", temp_dir], check=True)

    with zipfile.ZipFile(zip_path, "w") as z:
        for f in os.listdir(temp_dir):
            if f.endswith(".pdf"): z.write(os.path.join(temp_dir, f), f)
    return FileResponse(zip_path, filename="office_converted.zip")

# --- IMAGES -> PDF ---
@app.post("/convert/images-to-pdf")
async def images_to_pdf(files: List[UploadFile] = File(...)):
    temp_dir = tempfile.mkdtemp()
    output_pdf = os.path.join(temp_dir, "images_merged.pdf")
    image_list = []
    
    for file in files:
        img_p = os.path.join(temp_dir, file.filename)
        with open(img_p, "wb") as f: shutil.copyfileobj(file.file, f)
        image_list.append(Image.open(img_p).convert("RGB"))
    
    if image_list:
        image_list[0].save(output_pdf, save_all=True, append_images=image_list[1:])
        
    return FileResponse(output_pdf, filename="converted_images.pdf")

# --- PDF -> EXCEL ---
@app.post("/convert/pdf-to-excel")
async def pdf_to_excel(files: List[UploadFile] = File(...)):
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "pdf_excel.zip")
    
    with zipfile.ZipFile(zip_path, "w") as z:
        for file in files:
            p = os.path.join(temp_dir, file.filename)
            with open(p, "wb") as f: shutil.copyfileobj(file.file, f)
            out_xlsx = p.replace(".pdf", ".xlsx")
            # Utilisation de Camelot
            tables = camelot.read_pdf(p, pages="all")
            tables.export(out_xlsx, f="excel")
            if os.path.exists(out_xlsx): 
                z.write(out_xlsx, os.path.basename(out_xlsx))
            
    return FileResponse(zip_path, filename="excel_files.zip")
