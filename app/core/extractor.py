import re
from typing import List, Dict, Any
from app.models.schemas import InvoiceData, LineItem
from app.core.ocr import get_data_from_image, get_text_from_image
from app.core.utils import preprocess_image
from PIL import Image

def extract_invoice_data(image: Image.Image) -> InvoiceData:
    # Preprocess
    processed_image = preprocess_image(image)
    
    # Get full text for regex search
    full_text = get_text_from_image(processed_image)
    
    # Get detailed data for table parsing
    ocr_data = get_data_from_image(processed_image)
    
    # Extract Line Items
    line_items = _extract_line_items(ocr_data)
    
    # Extract Totals
    totals = _extract_totals(full_text)
    
    # Validate and Construct Response
    grand_total = totals.get("grand_total", 0.0)
    
    # If no grand total found, sum line items
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
    
    # Simple heuristic: Group text by line number (top coordinate)
    # This is a basic implementation. For production, we'd need robust column detection.
    
    lines = {}
    for i in range(n_boxes):
        if int(ocr_data['conf'][i]) > 30: # Filter low confidence
            text = ocr_data['text'][i].strip()
            if not text:
                continue
                
            top = ocr_data['top'][i]
            # Group by Y-coordinate (with some tolerance)
            found_line = False
            for y in lines.keys():
                if abs(y - top) < 10: # 10px tolerance
                    lines[y].append(text)
                    found_line = True
                    break
            if not found_line:
                lines[top] = [text]
                
    # Sort lines by Y-coordinate
    sorted_lines = sorted(lines.items())
    
    # Parse each line to find potential line items
    # Looking for lines that end with a number (amount)
    for _, words in sorted_lines:
        line_text = " ".join(words)
        
        # Regex for a line item: Description ... Amount
        # Assumes Amount is at the end
        match = re.search(r'(.+?)\s+(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)$', line_text)
        if match:
            description = match.group(1).strip()
            amount_str = match.group(2).replace(',', '')
            try:
                amount = float(amount_str)
                # Filter out likely headers or totals
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
    
    # Regex patterns
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
                # Take the last match as it's often the final total at the bottom
                try:
                    amount_str = matches[-1].replace(',', '')
                    totals[key] = float(amount_str)
                    break 
                except ValueError:
                    continue
                    
    return totals
