# Finance OCR

## Overview
A robust API to extract line items and totals from healthcare invoices using Tesseract OCR and FastAPI.

## Features
-   **Multi-format Support**: Handles PDF and Image inputs.
-   **Intelligent Extraction**: Extracts line items, sub-totals, tax, and grand totals.
-   **Preprocessing**: Enhances image quality for better OCR results.
-   **FastAPI Powered**: High-performance, async API.

## Setup

1.  **Install Dependencies**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
    *Note: Requires `tesseract` and `poppler` installed on the system.*

2.  **Run API**:
    ```bash
    uvicorn app.main:app --reload
    ```

## Usage

**Endpoint**: `POST /extract`

```bash
curl -X POST "http://localhost:8000/extract" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@Data/sample_1.png"
```

## Project Structure
-   `app/`: Source code
    -   `core/`: OCR and extraction logic
    -   `models/`: Pydantic schemas
    -   `main.py`: API entry point
-   `Data/`: Sample invoices