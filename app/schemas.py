# app/schemas.py
from pydantic import BaseModel
from typing import Optional, Dict, Any

class ProcessResponse(BaseModel):
    id: Optional[int]
    filename: Optional[str]
    doc_type: Optional[str]
    confidence: Optional[float]
    raw_text: Optional[str]
    extracted: Optional[Dict[str, Any]]
