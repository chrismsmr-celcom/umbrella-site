from fastapi import FastAPI, UploadFile, File, HTTPException, Form, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pdf2docx import Converter
from pdf2image import convert_from_path
from docx import Document
from pypdf import PdfWriter, PdfReader
from typing import List
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
import tempfile, os, shutil, zipfile, subprocess, pytesseract, uuid, camelot

app = FastAPI(title="Umbrella PDF Engine PRO")

# --- CONFIGURATION CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration binaire LibreOffice pour Render (Dockerfile nogui)
LIBREOFFICE_BIN = "soffice"

# --- UTILITAIRES ---

def cleanup(temp_dir: str):
    """Supprime le dossier temporaire après la réponse pour économiser le disque"""
    try:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
    except Exception as e:
        print(f"Erreur lors du nettoyage : {e}")

def process_pdf_to_word(pdf_path, docx_path):
    """Conversion PDF -> Word avec Fallback OCR si le texte est absent"""
    try:
        # 1. Conversion native
        cv = Converter(pdf_path)
        cv.convert(docx_path, start=0, end=None)
        cv.close()

        # 2. Détection de PDF scanné (seuil 5KB)
        if not os.path.exists(docx_path) or os.path.getsize(docx_path) < 5000:
            doc = Document()
            pages = convert_from_path(pdf_path, thread_count=1, dpi=150) 
            for i, page in enumerate(pages):
                text = pytesseract.image_to_string(page, lang='fra+eng')
                doc.add_paragraph(text)
                if i < len(pages) - 1:
                    doc.add_page_break()
                page.close() 
            doc.save(docx_path)
        return docx_path
    except Exception as e:
        print(f"Erreur process_pdf_to_word: {e}")
        return None

@app.get("/")
def root():
    return {"status": "Umbrella Engine Online", "environment": "Production-Ready"}

# --- CATEGORIE : CONVERSION (TO PDF) ---

@app.post("/convert/office-to-pdf")
async def office_to_pdf(background_tasks: BackgroundTasks, files: List[UploadFile] = File(...)):
    temp_dir = tempfile.mkdtemp()
    user_profile = os.path.join(temp_dir, "profile")
    try:
        for file in files:
            safe_name = f"{uuid.uuid4()}_{file.filename.replace(' ', '_')}"
            in_p = os.path.join(temp_dir, safe_name)
            with open(in_p, "wb") as f:
                shutil.copyfileobj(file.file, f)
            
            subprocess.run([
                LIBREOFFICE_BIN, "--headless", "--nodefault", "--nofirststartwizard",
                f"-env:UserInstallation=file://{user_profile}",
                "--convert-to", "pdf", in_p, "--outdir", temp_dir
            ], check=True, timeout=120)

        zip_path = os.path.join(temp_dir, "umbrella_office.zip")
        with zipfile.ZipFile(zip_path, "w") as z:
            for f in os.listdir(temp_dir):
                if f.lower().endswith(".pdf"):
                    z.write(os.path.join(temp_dir, f), f)
        
        background_tasks.add_task(cleanup, temp_dir)
        return FileResponse(zip_path, filename="umbrella_office_converted.zip", background=background_tasks)
    except Exception as e:
        cleanup(temp_dir)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/convert/images-to-pdf")
async def images_to_pdf(background_tasks: BackgroundTasks, files: List[UploadFile] = File(...)):
    temp_dir = tempfile.mkdtemp()
    output_pdf = os.path.join(temp_dir, "merged_images.pdf")
    try:
        img_objs = []
        for file in files:
            path = os.path.join(temp_dir, f"{uuid.uuid4()}_{file.filename}")
            with open(path, "wb") as f: shutil.copyfileobj(file.file, f)
            img_objs.append(Image.open(path).convert("RGB"))
        
        if img_objs:
            img_objs[0].save(output_pdf, save_all=True, append_images=img_objs[1:])
            for img in img_objs: img.close()
        
        background_tasks.add_task(cleanup, temp_dir)
        return FileResponse(output_pdf, filename="images_to_pdf.pdf", background=background_tasks)
    except Exception as e:
        cleanup(temp_dir)
        raise HTTPException(status_code=500, detail=str(e))

# --- CATEGORIE : CONVERSION (FROM PDF) ---

@app.post("/convert/pdf-to-word")
async def pdf_to_word(background_tasks: BackgroundTasks, files: List[UploadFile] = File(...)):
    temp_dir = tempfile.mkdtemp()
    try:
        tasks = []
        for file in files:
            p = os.path.join(temp_dir, f"{uuid.uuid4()}_{file.filename}")
            d = p.rsplit(".", 1)[0] + ".docx"
            with open(p, "wb") as f: shutil.copyfileobj(file.file, f)
            tasks.append((p, d))
        
        with ThreadPoolExecutor(max_workers=2) as ex:
            list(ex.map(lambda t: process_pdf_to_word(*t), tasks))
        
        zip_path = os.path.join(temp_dir, "umbrella_word.zip")
        with zipfile.ZipFile(zip_path, "w") as z:
            for f in os.listdir(temp_dir):
                if f.endswith(".docx"): z.write(os.path.join(temp_dir, f), f)
        
        background_tasks.add_task(cleanup, temp_dir)
        return FileResponse(zip_path, filename="umbrella_word.zip", background=background_tasks)
    except Exception as e:
        cleanup(temp_dir)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/convert/ocr")
async def ocr_pdf(background_tasks: BackgroundTasks, files: List[UploadFile] = File(...)):
    temp_dir = tempfile.mkdtemp()
    try:
        zip_path = os.path.join(temp_dir, "umbrella_ocr.zip")
        with zipfile.ZipFile(zip_path, "w") as z:
            for file in files:
                p = os.path.join(temp_dir, f"{uuid.uuid4()}_{file.filename}")
                with open(p, "wb") as f: shutil.copyfileobj(file.file, f)
                
                pages = convert_from_path(p, thread_count=1, dpi=150)
                doc = Document()
                for page in pages:
                    text = pytesseract.image_to_string(page, lang='fra+eng')
                    doc.add_paragraph(text)
                    page.close()
                
                out_docx = p.replace(".pdf", "_ocr.docx")
                doc.save(out_docx)
                z.write(out_docx, os.path.basename(out_docx))
        
        background_tasks.add_task(cleanup, temp_dir)
        return FileResponse(zip_path, filename="umbrella_ocr_results.zip", background=background_tasks)
    except Exception as e:
        cleanup(temp_dir)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/convert/pdf-to-excel")
async def pdf_to_excel(background_tasks: BackgroundTasks, files: List[UploadFile] = File(...)):
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "umbrella_excel.zip")
    try:
        with zipfile.ZipFile(zip_path, "w") as z:
            for file in files:
                p = os.path.join(temp_dir, f"{uuid.uuid4()}_{file.filename}")
                with open(p, "wb") as f: shutil.copyfileobj(file.file, f)
                out_xlsx = p.replace(".pdf", ".xlsx")
                tables = camelot.read_pdf(p, pages="all", flavor='stream')
                tables.export(out_xlsx, f="excel")
                if os.path.exists(out_xlsx):
                    z.write(out_xlsx, os.path.basename(out_xlsx))
        
        background_tasks.add_task(cleanup, temp_dir)
        return FileResponse(zip_path, filename="umbrella_excel.zip", background=background_tasks)
    except Exception as e:
        cleanup(temp_dir)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/convert/pdf-to-jpg")
async def pdf_to_jpg(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    temp_dir = tempfile.mkdtemp()
    try:
        p = os.path.join(temp_dir, f"{uuid.uuid4()}_{file.filename}")
        with open(p, "wb") as f: shutil.copyfileobj(file.file, f)
        image_paths = convert_from_path(p, dpi=150, output_folder=temp_dir, fmt="jpg", paths_only=True)
        
        zip_path = os.path.join(temp_dir, "images.zip")
        with zipfile.ZipFile(zip_path, "w") as z:
            for i, path in enumerate(image_paths):
                z.write(path, f"page_{i+1}.jpg")
        
        background_tasks.add_task(cleanup, temp_dir)
        return FileResponse(zip_path, filename="pdf_images.zip", background=background_tasks)
    except Exception as e:
        cleanup(temp_dir)
        raise HTTPException(status_code=500, detail=str(e))

# --- CATEGORIE : ORGANISATION & SECURITE ---

@app.post("/organize/merge")
async def merge_pdfs(background_tasks: BackgroundTasks, files: List[UploadFile] = File(...)):
    temp_dir = tempfile.mkdtemp()
    merger = PdfWriter()
    try:
        for file in files:
            p = os.path.join(temp_dir, f"{uuid.uuid4()}_{file.filename}")
            with open(p, "wb") as f: shutil.copyfileobj(file.file, f)
            merger.append(p)
        
        out = os.path.join(temp_dir, "merged.pdf")
        merger.write(out)
        merger.close()
        background_tasks.add_task(cleanup, temp_dir)
        return FileResponse(out, filename="merged.pdf", background=background_tasks)
    except Exception as e:
        cleanup(temp_dir)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/organize/split")
async def split_pdf(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    temp_dir = tempfile.mkdtemp()
    try:
        p = os.path.join(temp_dir, f"{uuid.uuid4()}_{file.filename}")
        with open(p, "wb") as f: shutil.copyfileobj(file.file, f)
        
        reader = PdfReader(p)
        zip_path = os.path.join(temp_dir, "split_pages.zip")
        with zipfile.ZipFile(zip_path, "w") as z:
            for i, page in enumerate(reader.pages):
                writer = PdfWriter()
                writer.add_page(page)
                page_path = os.path.join(temp_dir, f"page_{i+1}.pdf")
                with open(page_path, "wb") as f: writer.write(f)
                z.write(page_path, f"page_{i+1}.pdf")
        
        background_tasks.add_task(cleanup, temp_dir)
        return FileResponse(zip_path, filename="split_pdf.zip", background=background_tasks)
    except Exception as e:
        cleanup(temp_dir)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/security/protect")
async def protect_pdf(background_tasks: BackgroundTasks, file: UploadFile = File(...), password: str = Form(...)):
    temp_dir = tempfile.mkdtemp()
    try:
        p = os.path.join(temp_dir, file.filename)
        with open(p, "wb") as f: shutil.copyfileobj(file.file, f)
        
        reader = PdfReader(p)
        writer = PdfWriter()
        for page in reader.pages: writer.add_page(page)
        writer.encrypt(password)
        
        out = os.path.join(temp_dir, "protected.pdf")
        with open(out, "wb") as f: writer.write(f)
        
        background_tasks.add_task(cleanup, temp_dir)
        return FileResponse(out, filename="protected.pdf", background=background_tasks)
    except Exception as e:
        cleanup(temp_dir)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/edit/repair")
async def repair_pdf(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    temp_dir = tempfile.mkdtemp()
    try:
        p = os.path.join(temp_dir, file.filename)
        with open(p, "wb") as f: shutil.copyfileobj(file.file, f)
        reader = PdfReader(p)
        writer = PdfWriter()
        for page in reader.pages: writer.add_page(page)
        out = os.path.join(temp_dir, "repaired.pdf")
        with open(out, "wb") as f: writer.write(f)
        background_tasks.add_task(cleanup, temp_dir)
        return FileResponse(out, filename="repaired_fixed.pdf", background=background_tasks)
    except Exception as e:
        cleanup(temp_dir)
        raise HTTPException(status_code=500, detail="Fichier trop corrompu.")

@app.post("/edit/unlock")
async def unlock_pdf(background_tasks: BackgroundTasks, file: UploadFile = File(...), password: str = Form(None)):
    temp_dir = tempfile.mkdtemp()
    try:
        p = os.path.join(temp_dir, file.filename)
        with open(p, "wb") as f: shutil.copyfileobj(file.file, f)
        reader = PdfReader(p)
        if reader.is_encrypted:
            if password: reader.decrypt(password)
            else: raise HTTPException(status_code=400, detail="Mot de passe requis.")
        
        writer = PdfWriter()
        for page in reader.pages: writer.add_page(page)
        out = os.path.join(temp_dir, "unlocked.pdf")
        with open(out, "wb") as f: writer.write(f)
        background_tasks.add_task(cleanup, temp_dir)
        return FileResponse(out, filename="unlocked.pdf", background=background_tasks)
    except Exception as e:
        cleanup(temp_dir)
        raise HTTPException(status_code=500, detail="Erreur de décryptage.")
