"""
Standalone FastAPI application for Document Intelligence System.
Run with: uvicorn main_standalone:app --reload
"""
import os
import sys
import tempfile
from pathlib import Path
from fastapi import FastAPI, UploadFile, HTTPException, File
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import traceback

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent / "app"))

# Import modules
import ocr
import classifier
import extractor
import text_processor
from config import ALLOWED_EXTENSIONS, UPLOAD_MAX_SIZE

load_dotenv()

app = FastAPI(title="Document Intelligence API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Document Intelligence API",
        "version": "1.0.0",
        "endpoints": ["/process", "/health"],
        "supported_types": ["invoice", "cv", "id_card", "receipt"]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "document-intelligence"}

@app.post("/process")
async def process_document(file: UploadFile = File(...)):
    """Process uploaded document: OCR → Classify → Extract fields."""
    
    tmp_path = None
    try:
        # Validate file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_ext} not allowed. Allowed: {list(ALLOWED_EXTENSIONS)}"
            )
        
        # Read file content
        content = await file.read()
        
        # Validate file size
        if len(content) > UPLOAD_MAX_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size: {UPLOAD_MAX_SIZE / 1024 / 1024}MB"
            )
        
        # Save temp file
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=file_ext)
        tmp.write(content)
        tmp.close()
        tmp_path = tmp.name
        
        # Step 1: OCR
        text = ocr.run_ocr(tmp_path)
        if not text or len(text.strip()) < 10:
            raise HTTPException(status_code=400, detail="Could not extract text from document")
        
        # Step 2: Clean text
        cleaned = text_processor.clean_text(text)
        
        # Step 3: Classify
        doc_type, confidence = classifier.classify_document(cleaned)
        
        # Step 4: Extract fields
        extracted_json = extractor.extract_fields(doc_type, cleaned)
        
        return {
            "success": True,
            "filename": file.filename,
            "document_type": doc_type,
            "confidence": confidence,
            "extracted_data": extracted_json,
            "raw_text": cleaned[:500],  # Preview
        }
    
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
    
    finally:
        # Cleanup temp file
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except:
                pass

# Note: Do NOT add uvicorn.run() here when using --reload
# Run with: uvicorn main_standalone:app --reload --port 8000
