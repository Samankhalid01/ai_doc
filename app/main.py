import os
import tempfile
from fastapi import FastAPI, UploadFile, HTTPException, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from supabase import create_client
from .ocr import run_ocr
from .classifier import classify_document
from .extractor import extract_fields
from .text_processor import clean_text
from .config import SUPABASE_URL, SUPABASE_KEY, SUPABASE_BUCKET, ALLOWED_EXTENSIONS, UPLOAD_MAX_SIZE
from dotenv import load_dotenv
import traceback
from pathlib import Path

load_dotenv()

# Initialize Supabase (optional if using Supabase)
supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="Document Intelligence API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "Document Intelligence API",
        "version": "1.0.0",
        "endpoints": ["/process", "/health"]
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
                detail=f"File type {file_ext} not allowed. Allowed: {ALLOWED_EXTENSIONS}"
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
        
        # Upload to Supabase Storage (optional)
        file_url = None
        if supabase:
            try:
                supabase.storage.from_(SUPABASE_BUCKET).upload(
                    file.filename, tmp_path, {"content-type": file.content_type}
                )
                file_url = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(file.filename)
            except Exception as e:
                print(f"Supabase upload warning: {e}")
        
        # Step 1: OCR
        text = run_ocr(tmp_path)
        if not text or len(text.strip()) < 10:
            raise HTTPException(status_code=400, detail="Could not extract text from document")
        
        # Step 2: Clean text
        cleaned = clean_text(text)
        
        # Step 3: Classify
        doc_type, confidence = classify_document(cleaned)
        
        # Step 4: Extract fields
        extracted_json = extract_fields(doc_type, cleaned)
        
        # Save to Supabase DB (optional)
        if supabase:
            try:
                supabase.table("documents").insert({
                    "filename": file.filename,
                    "document_type": doc_type,
                    "original_url": file_url,
                    "extracted_text": cleaned[:1000],  # Limit text size
                    "extracted_json": extracted_json
                }).execute()
            except Exception as e:
                print(f"Supabase DB warning: {e}")
        
        return {
            "success": True,
            "filename": file.filename,
            "document_type": doc_type,
            "confidence": confidence,
            "extracted_data": extracted_json,
            "raw_text": cleaned[:500],  # Preview
            "file_url": file_url
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
