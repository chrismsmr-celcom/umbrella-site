from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from pdf2docx import Converter
from pdf2image import convert_from_path
from PIL import Image
from docx import Document
from io import BytesIO
import os

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- PDF -> Word ---
@app.post("/pdf2word")
async def pdf_to_word(file: UploadFile = File(...)):
    input_path = os.path.join(UPLOAD_DIR, file.filename)
    output_path = os.path.join(UPLOAD_DIR, file.filename.replace(".pdf", ".docx"))

    with open(input_path, "wb") as f:
        f.write(await file.read())

    cv = Converter(input_path)
    cv.convert(output_path, start=0, end=None)
    cv.close()

    return FileResponse(output_path, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", filename=os.path.basename(output_path))

# --- Word -> PDF ---
@app.post("/word2pdf")
async def word_to_pdf(file: UploadFile = File(...)):
    input_path = os.path.join(UPLOAD_DIR, file.filename)
    output_path = os.path.join(UPLOAD_DIR, file.filename.replace(".docx", ".pdf"))

    with open(input_path, "wb") as f:
        f.write(await file.read())

    # Lire Word et convertir en PDF via ReportLab
    doc = Document(input_path)
    pdf_buffer = BytesIO()
    from reportlab.pdfgen import canvas
    c = canvas.Canvas(pdf_buffer)
    y = 800
    for para in doc.paragraphs:
        c.drawString(50, y, para.text)
        y -= 15
    c.save()
    pdf_buffer.seek(0)

    with open(output_path, "wb") as f:
        f.write(pdf_buffer.read())

    return FileResponse(output_path, media_type="application/pdf", filename=os.path.basename(output_path))

# --- PDF -> Image ---
@app.post("/pdf2image")
async def pdf_to_image(file: UploadFile = File(...)):
    input_path = os.path.join(UPLOAD_DIR, file.filename)
    output_path = os.path.join(UPLOAD_DIR, file.filename.replace(".pdf", ".png"))

    with open(input_path, "wb") as f:
        f.write(await file.read())

    images = convert_from_path(input_path)
    images[0].save(output_path, "PNG")

    return FileResponse(output_path, media_type="image/png", filename=os.path.basename(output_path))

# --- Image -> PDF ---
@app.post("/image2pdf")
async def image_to_pdf(file: UploadFile = File(...)):
    input_path = os.path.join(UPLOAD_DIR, file.filename)
    output_path = os.path.join(UPLOAD_DIR, file.filename.rsplit(".", 1)[0] + ".pdf")

    with open(input_path, "wb") as f:
        f.write(await file.read())

    image = Image.open(input_path).convert("RGB")
    image.save(output_path, "PDF")

    return FileResponse(output_path, media_type="application/pdf", filename=os.path.basename(output_path))
