from fastapi import FastAPI, UploadFile, File, HTTPException
from app.models.schemas import ExtractionResponse, InvoiceData
from app.core.extractor import extract_invoice_data
from pdf2image import convert_from_bytes
from PIL import Image
import io
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Bajaj OCR API", description="Extracts data from invoices")

@app.post("/extract", response_model=ExtractionResponse)
async def extract_data(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        images = []
        if file.content_type == "application/pdf":
            try:
                images = convert_from_bytes(contents)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid PDF: {str(e)}")
        elif file.content_type.startswith("image/"):
            try:
                image = Image.open(io.BytesIO(contents))
                images = [image]
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid Image: {str(e)}")
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Upload PDF or Image.")

        if not images:
             raise HTTPException(status_code=400, detail="No content found in file.")

        all_line_items = []
        grand_total = 0.0
        sub_total = 0.0
        tax = 0.0
        found_totals = []
        for i, img in enumerate(images):
            logger.info(f"Processing page {i+1}")
            data = extract_invoice_data(img)
            all_line_items.extend(data.line_items)
            if data.grand_total > 0:
                found_totals.append(data.grand_total)
            if data.sub_total:
                sub_total = max(sub_total, data.sub_total)
            if data.tax:
                tax = max(tax, data.tax)

        if found_totals:
            grand_total = max(found_totals)
        else:
            grand_total = sum(item.amount for item in all_line_items)

        final_data = InvoiceData(
            line_items=all_line_items,
            sub_total=sub_total if sub_total > 0 else None,
            tax=tax if tax > 0 else None,
            grand_total=grand_total
        )

        return ExtractionResponse(
            filename=file.filename,
            data=final_data,
            success=True
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error processing file: {e}", exc_info=True)
        return ExtractionResponse(
            filename=file.filename,
            data=InvoiceData(line_items=[], grand_total=0.0),
            success=False,
            error=str(e)
        )

@app.get("/")
def read_root():
    return {"message": "Bajaj OCR API is running"}
