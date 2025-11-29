# Finance OCR - Pitch Deck

## 1. Problem Statement
**Objective**: Automate the extraction of line items and totals from diverse healthcare invoices (OPD/IPD).
**Challenge**: High volume of bills, varying formats (images/PDFs), noise, and potential fraud.
**Impact**: Reduce manual processing time, minimize errors, and ensure accurate claims settlement.

## 2. Solution Architecture
Our solution leverages a robust, modular pipeline designed for accuracy and scalability.

-   **Input Layer**: Handles multi-page PDFs and Images.
-   **Preprocessing Engine**:
    -   Grayscale conversion & Thresholding (Otsu's method) to enhance text clarity.
    -   Noise reduction to handle scanned documents.
-   **OCR Core**: Tesseract 5 (LSTM) for high-accuracy text recognition.
-   **Extraction Logic**:
    -   **Spatial Analysis**: Groups text by Y-coordinates to reconstruct rows.
    -   **Regex Heuristics**: Identifies totals, taxes, and line item amounts with high precision.
-   **API Layer**: FastAPI-based REST API for seamless integration.

## 3. Tech Stack
-   **Backend**: Python 3.10+, FastAPI
-   **OCR**: Tesseract, Pytesseract
-   **Image Processing**: OpenCV, Pillow, pdf2image
-   **Deployment**: Docker-ready, Uvicorn

## 4. Differentiators
-   **Preprocessing Pipeline**: Specifically tuned for scanned medical bills, handling noise and skew.
-   **Hybrid Extraction**: Combines spatial layout analysis with regex pattern matching to handle both structured tables and unstructured summaries.
-   **Fraud Detection Ready**: Architecture allows easy plugging of font-consistency checks (future scope).

## 5. Performance & Roadmap
-   **Latency**: < 2s per page on standard CPU.
-   **Accuracy**: High precision on standard formats.
-   **Future Scope**:
    -   Integration with Vision LLMs (GPT-4o) for handwriting.
    -   Graph Neural Networks (GNNs) for table structure recognition.
