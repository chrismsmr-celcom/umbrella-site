from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pdf2docx import Converter
from pdf2image import convert_from_path
from docx import Document
from pypdf import PdfWriter, PdfReader
from typing import List
from concurrent.futures import ThreadPoolExecutor
import tempfile, os, shutil, zipfile, subprocess, pytesseract, camelot
from PIL import Image

app = FastAPI(title="Umbrella PDF Engine PRO")

# --- CONFIGURATION CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

LIBREOFFICE_BIN = "soffice"

@app.get("/")
def root():
    return {
        "status": "Umbrella Engine Online", 
        "environment": "Docker Linux OCR-Ready",
        "endpoints": ["/organize", "/convert", "/security"]
    }

# --- LOGIQUE PDF -> WORD AVEC OCR HYBRIDE ---
def process_pdf_to_word(pdf_path, docx_path):
    try:
        # 1. Tentative avec pdf2docx (pour conserver le layout)
        cv = Converter(pdf_path)
        cv.convert(docx_path, start=0, end=None)
        cv.close()

        # 2. Détection de scan (si le fichier résultant est quasi vide, on lance l'OCR)
        if os.path.exists(docx_path) and os.path.getsize(docx_path) < 5000:
            doc = Document()
            pages = convert_from_path(pdf_path)
            for i, page in enumerate(pages):
                text = pytesseract.image_to_string(page, lang='fra+eng', config='--psm 1')
                doc.add_paragraph(text)
                if i < len(pages) - 1:
                    doc.add_page_break()
            doc.save(docx_path)
            
        return docx_path
    except Exception as e:
        print(f"Erreur technique sur {pdf_path} : {e}")
        return None

# --- CATEGORIE : CONVERT ---

@app.post("/convert/pdf-to-word")
async def pdf_to_word(files: List[UploadFile] = File(...)):
    temp_dir = tempfile.mkdtemp()
    try:
        zip_path = os.path.join(temp_dir, "umbrella_word.zip")
        tasks = []
        for file in files:
            p = os.path.join(temp_dir, file.filename)
            d = p.replace(".pdf", ".docx")
            with open(p, "wb") as f:
                shutil.copyfileobj(file.file, f)
            tasks.append((p, d))
        
        with ThreadPoolExecutor() as ex:
            results = list(ex.map(lambda t: process_pdf_to_word(*t), tasks))
        
        with zipfile.ZipFile(zip_path, "w") as z:
            for r in [res for res in results if res]:
                z.write(r, os.path.basename(r))
        
        return FileResponse(zip_path, filename="umbrella_converted_word.zip")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/convert/office-to-pdf")
async def office_to_pdf(files: List[UploadFile] = File(...)):
    temp_dir = tempfile.mkdtemp()
    try:
        for file in files:
            in_p = os.path.join(temp_dir, file.filename)
            with open(in_p, "wb") as f: 
                shutil.copyfileobj(file.file, f)
            subprocess.run([LIBREOFFICE_BIN, "--headless", "--convert-to", "pdf", in_p, "--outdir", temp_dir], check=True)

        zip_path = os.path.join(temp_dir, "umbrella_office.zip")
        with zipfile.ZipFile(zip_path, "w") as z:
            for f in os.listdir(temp_dir):
                if f.endswith(".pdf"): 
                    z.write(os.path.join(temp_dir, f), f)
        return FileResponse(zip_path, filename="umbrella_converted_office.zip")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/convert/pdf-to-excel")
async def pdf_to_excel(files: List[UploadFile] = File(...)):
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "umbrella_excel.zip")
    try:
        with zipfile.ZipFile(zip_path, "w") as z:
            for file in files:
                p = os.path.join(temp_dir, file.filename)
                with open(p, "wb") as f: 
                    shutil.copyfileobj(file.file, f)
                out_xlsx = p.replace(".pdf", ".xlsx")
                tables = camelot.read_pdf(p, pages="all")
                tables.export(out_xlsx, f="excel")
                if os.path.exists(out_xlsx): 
                    z.write(out_xlsx, os.path.basename(out_xlsx))
        return FileResponse(zip_path, filename="umbrella_excel.zip")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/convert/pdf-to-jpg")
async def pdf_to_jpg(file: UploadFile = File(...)):
    temp_dir = tempfile.mkdtemp()
    try:
        p = os.path.join(temp_dir, file.filename)
        with open(p, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        images = convert_from_path(p)
        zip_path = os.path.join(temp_dir, "umbrella_images.zip")
        
        with zipfile.ZipFile(zip_path, "w") as z:
            for i, img in enumerate(images):
                img_name = f"page_{i+1}.jpg"
                img_path = os.path.join(temp_dir, img_name)
                img.save(img_path, "JPEG")
                z.write(img_path, img_name)
                
        return FileResponse(zip_path, filename="umbrella_pdf_to_jpg.zip")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/convert/images-to-pdf")
async def images_to_pdf(files: List[UploadFile] = File(...)):
    temp_dir = tempfile.mkdtemp()
    output_pdf = os.path.join(temp_dir, "images_merged.pdf")
    try:
        image_list = []
        for file in files:
            img_p = os.path.join(temp_dir, file.filename)
            with open(img_p, "wb") as f: 
                shutil.copyfileobj(file.file, f)
            image_list.append(Image.open(img_p).convert("RGB"))
        if image_list:
            image_list[0].save(output_pdf, save_all=True, append_images=image_list[1:])
        return FileResponse(output_pdf, filename="umbrella_images.pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- CATEGORIE : ORGANIZE ---

@app.post("/organize/merge")
async def merge_pdfs(files: List[UploadFile] = File(...)):
    temp_dir = tempfile.mkdtemp()
    merger = PdfWriter()
    output_path = os.path.join(temp_dir, "merged.pdf")
    try:
        for file in files:
            p = os.path.join(temp_dir, file.filename)
            with open(p, "wb") as f: 
                shutil.copyfileobj(file.file, f)
            merger.append(p)
        merger.write(output_path)
        merger.close()
        return FileResponse(output_path, filename="umbrella_merged.pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/organize/split")
async def split_pdf(file: UploadFile = File(...)):
    temp_dir = tempfile.mkdtemp()
    try:
        p = os.path.join(temp_dir, file.filename)
        with open(p, "wb") as f: 
            shutil.copyfileobj(file.file, f)
        
        reader = PdfReader(p)
        zip_path = os.path.join(temp_dir, "split.zip")
        with zipfile.ZipFile(zip_path, "w") as z:
            for i, page in enumerate(reader.pages):
                writer = PdfWriter()
                writer.add_page(page)
                page_path = os.path.join(temp_dir, f"page_{i+1}.pdf")
                with open(page_path, "wb") as f_out: 
                    writer.write(f_out)
                z.write(page_path, os.path.basename(page_path))
        return FileResponse(zip_path, filename="umbrella_split.zip")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- CATEGORIE : SECURITY ---

@app.post("/security/protect")
async def protect_pdf(file: UploadFile = File(...), password: str = Form("umbrella123")):
    temp_dir = tempfile.mkdtemp()
    try:
        p = os.path.join(temp_dir, file.filename)
        with open(p, "wb") as f: 
            shutil.copyfileobj(file.file, f)
            
        reader = PdfReader(p)
        writer = PdfWriter()
        for page in reader.pages: 
            writer.add_page(page)
        
        writer.encrypt(password)
        protected_path = os.path.join(temp_dir, "locked_" + file.filename)
        with open(protected_path, "wb") as f_out: 
            writer.write(f_out)
            
        return FileResponse(protected_path, filename="umbrella_protected.pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
