import re
from typing import List, Dict, Any
from app.models.schemas import InvoiceData, LineItem
from app.core.ocr import get_data_from_image, get_text_from_image
from app.core.utils import preprocess_image
from PIL import Image

def extract_invoice_data(image: Image.Image) -> InvoiceData:
    processed_image = preprocess_image(image)
    full_text = get_text_from_image(processed_image)
    ocr_data = get_data_from_image(processed_image)
    line_items = _extract_line_items(ocr_data)
    totals = _extract_totals(full_text)
    grand_total = totals.get("grand_total", 0.0)
    calculated_total = sum(item.amount for item in line_items)
    if grand_total == 0.0:
        grand_total = calculated_total
    return InvoiceData(
        line_items=line_items,
        sub_total=totals.get("sub_total"),
        tax=totals.get("tax"),
        grand_total=grand_total
    )

def _extract_line_items(ocr_data: Dict[str, Any]) -> List[LineItem]:
    line_items = []
    n_boxes = len(ocr_data['text'])
    lines: Dict[int, List[str]] = {}
    for i in range(n_boxes):
        if int(ocr_data['conf'][i]) > 30:
            text = ocr_data['text'][i].strip()
            if not text:
                continue
            top = ocr_data['top'][i]
            found_line = False
            for y in lines.keys():
                if abs(y - top) < 10:
                    lines[y].append(text)
                    found_line = True
                    break
            if not found_line:
                lines[top] = [text]
    sorted_lines = sorted(lines.items())
    for _, words in sorted_lines:
        line_text = " ".join(words)
        match = re.search(r'(.+?)\s+(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)$', line_text)
        if match:
            description = match.group(1).strip()
            amount_str = match.group(2).replace(',', '')
            try:
                amount = float(amount_str)
                if "total" in description.lower() or "amount" in description.lower():
                    continue
                line_items.append(LineItem(
                    description=description,
                    amount=amount
                ))
            except ValueError:
                continue
    return line_items

def _extract_totals(text: str) -> Dict[str, float]:
    totals = {}
    patterns = {
        "grand_total": [
            r"Total\s*[:\-\s]\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)",
            r"Grand Total\s*[:\-\s]\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)",
            r"Net Amt\s*[:\-\s]\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)"
        ],
        "sub_total": [
            r"Sub\s*Total\s*[:\-\s]\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)"
        ],
        "tax": [
            r"Tax\s*[:\-\s]\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)",
            r"GST\s*[:\-\s]\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)"
        ]
    }
    for key, pattern_list in patterns.items():
        for pattern in pattern_list:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    amount_str = matches[-1].replace(',', '')
                    totals[key] = float(amount_str)
                    break 
                except ValueError:
                    continue
    return totals
