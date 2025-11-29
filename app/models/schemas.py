from pydantic import BaseModel
from typing import List, Optional

class LineItem(BaseModel):
    description: str
    quantity: Optional[float] = None
    rate: Optional[float] = None
    amount: float

class InvoiceData(BaseModel):
    line_items: List[LineItem]
    sub_total: Optional[float] = None
    tax: Optional[float] = None
    grand_total: float
    warnings: List[str] = []

class ExtractionResponse(BaseModel):
    filename: str
    data: InvoiceData
    success: bool
    error: Optional[str] = None
