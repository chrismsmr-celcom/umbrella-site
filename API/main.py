from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from pdf2docx import Converter
from PIL import Image
import os

app = FastAPI()

# Dossier pour stocker les fichiers uploadés et convertis
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- PDF → Word ---
@app.post("/pdf2word")
async def pdf_to_word(file: UploadFile = File(...)):
    try:
        input_path = os.path.join(UPLOAD_DIR, file.filename)
        output_path = os.path.join(UPLOAD_DIR, file.filename.replace(".pdf", ".docx"))

        # Sauvegarde du fichier PDF
        with open(input_path, "wb") as f:
            f.write(await file.read())

        # Conversion PDF → Word
        cv = Converter(input_path)
        cv.convert(output_path, start=0, end=None)
        cv.close()

        return FileResponse(
            output_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=os.path.basename(output_path)
        )
    except Exception as e:
        return {"error": str(e)}

# --- Image → PDF ---
@app.post("/image2pdf")
async def image_to_pdf(file: UploadFile = File(...)):
    try:
        input_path = os.path.join(UPLOAD_DIR, file.filename)
        output_path = os.path.join(UPLOAD_DIR, file.filename.rsplit(".", 1)[0] + ".pdf")

        # Sauvegarde de l'image
        with open(input_path, "wb") as f:
            f.write(await file.read())

        # Conversion Image → PDF
        image = Image.open(input_path).convert("RGB")
        image.save(output_path, "PDF")

        return FileResponse(
            output_path,
            media_type="application/pdf",
            filename=os.path.basename(output_path)
        )
    except Exception as e:
        return {"error": str(e)}
