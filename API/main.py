from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pdf2docx import Converter
from pdf2image import convert_from_path
from pptx import Presentation
from PIL import Image
from typing import List
from concurrent.futures import ThreadPoolExecutor
import tempfile, os, shutil, zipfile, subprocess
import camelot

app = FastAPI(title="Umbrella PDF Engine")

# Configuration CORS pour ton Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sur Render/Linux, on utilise directement la commande système
LIBREOFFICE_BIN = "soffice"

@app.get("/")
def root():
    return {"status": "Umbrella Engine Online", "environment": "Docker Linux"}

# --- PDF -> WORD ---
def process_pdf_to_word(pdf_path, docx_path):
    try:
        cv = Converter(pdf_path)
        cv.convert(docx_path)
        cv.close()
        return docx_path
    except: return None

@app.post("/convert/pdf-to-word")
async def pdf_to_word(files: List[UploadFile] = File(...)):
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "converted_word.zip")
    tasks = []
    for file in files:
        p = os.path.join(temp_dir, file.filename)
        d = p.replace(".pdf", ".docx")
        with open(p, "wb") as f: shutil.copyfileobj(file.file, f)
        tasks.append((p, d))
    
    with ThreadPoolExecutor() as ex:
        results = list(ex.map(lambda t: process_pdf_to_word(*t), tasks))
    
    with zipfile.ZipFile(zip_path, "w") as z:
        for r in [res for res in results if res]:
            z.write(r, os.path.basename(r))
    return FileResponse(zip_path, filename="word_files.zip")

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

# --- IMAGES -> PDF ---
@app.post("/convert/images-to-pdf")
async def images_to_pdf(files: List[UploadFile] = File(...)):
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "images_to_pdf.zip")
    pdfs = []
    for file in files:
        img_p = os.path.join(temp_dir, file.filename)
        with open(img_p, "wb") as f: shutil.copyfileobj(file.file, f)
        pdf_p = img_p.rsplit(".", 1)[0] + ".pdf"
        Image.open(img_p).convert("RGB").save(pdf_p, "PDF")
        pdfs.append(pdf_p)
    
    with zipfile.ZipFile(zip_path, "w") as z:
        for p in pdfs: z.write(p, os.path.basename(p))
    return FileResponse(zip_path, filename="images_converted.zip")

# --- OFFICE (WORD/EXCEL/PPTX) -> PDF ---
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

# --- PDF -> EXCEL (CAMELOT) ---
@app.post("/convert/pdf-to-excel")
async def pdf_to_excel(files: List[UploadFile] = File(...)):
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "pdf_excel.zip")
    
    with zipfile.ZipFile(zip_path, "w") as z:
        for file in files:
            p = os.path.join(temp_dir, file.filename)
            with open(p, "wb") as f: shutil.copyfileobj(file.file, f)
            out_xlsx = p.replace(".pdf", ".xlsx")
            tables = camelot.read_pdf(p, pages="all")
            tables.export(out_xlsx, f="excel")
            # Camelot exporte souvent en nom_page_1.xlsx
            if os.path.exists(out_xlsx): z.write(out_xlsx, os.path.basename(out_xlsx))
            
    return FileResponse(zip_path, filename="excel_files.zip")
