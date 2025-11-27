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
import time
import uuid
import json
from pathlib import Path

load_dotenv()

# Initialize Supabase 
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
        
        # Upload to Supabase Storage (optional). Use unique destination name to avoid overwrites.
        file_url = None
        storage_path = None
        if supabase:
            try:
                dest_name = f"{int(time.time())}_{uuid.uuid4().hex}_{file.filename}"
                upload_resp = supabase.storage.from_(SUPABASE_BUCKET).upload(dest_name, tmp_path, {"content-type": file.content_type})
                print("Supabase upload response:", upload_resp)
                # get_public_url may return different shapes depending on client version
                public_resp = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(dest_name)
                if isinstance(public_resp, dict):
                    file_url = public_resp.get('publicUrl') or public_resp.get('publicURL') or public_resp.get('public_url')
                else:
                    file_url = str(public_resp)
                storage_path = dest_name
            except Exception as e:
                print(f"Supabase upload warning: {e}")
                file_url = None
                storage_path = None
        
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
        
        # Save to Supabase DB (optional). If Supabase is not configured, append to a local JSONL fallback file.
        if supabase:
            try:
                record = {
                    "filename": file.filename,
                    "storage_path": storage_path,
                    "file_url": file_url,
                    "document_type": doc_type,
                    "extracted_text": cleaned[:1000],
                    "extracted_json": extracted_json
                }
                insert_resp = supabase.table("documents").insert(record).execute()
                print("Supabase insert response:", insert_resp)
            except Exception as e:
                print(f"Supabase DB warning: {e}")
                # Try a reduced insert with only commonly-available columns (some schemas may not have extracted_json)
                try:
                    reduced = {
                        "filename": file.filename,
                        "document_type": doc_type,
                        "original_url": file_url,
                        "extracted_text": cleaned[:1000]
                    }
                    insert_resp2 = supabase.table("documents").insert(reduced).execute()
                    print("Supabase reduced insert response:", insert_resp2)
                except Exception as e2:
                    print(f"Supabase reduced insert failed: {e2}")
                    # On any Supabase failure, fall back to local persistence
                    try:
                        fallback = {
                            "id": uuid.uuid4().hex,
                            "timestamp": int(time.time()),
                            "filename": file.filename,
                            "storage_path": storage_path,
                            "file_url": file_url,
                            "document_type": doc_type,
                            "extracted_text": cleaned[:1000],
                            "extracted_json": extracted_json
                        }
                        with open("processed_documents.jsonl", "a", encoding="utf-8") as fh:
                            fh.write(json.dumps(fallback, ensure_ascii=False) + "\n")
                        print("Wrote fallback record to processed_documents.jsonl (after Supabase failure)")
                    except Exception as e3:
                        print(f"Local fallback write warning after Supabase failure: {e3}")
        else:
            # fallback local persistence (append JSONL)
            try:
                fallback = {
                    "id": uuid.uuid4().hex,
                    "timestamp": int(time.time()),
                    "filename": file.filename,
                    "document_type": doc_type,
                    "extracted_text": cleaned[:1000],
                    "extracted_json": extracted_json,
                    "file_url": None
                }
                with open("processed_documents.jsonl", "a", encoding="utf-8") as fh:
                    fh.write(json.dumps(fallback, ensure_ascii=False) + "\n")
                print("Wrote fallback record to processed_documents.jsonl")
            except Exception as e:
                print(f"Local fallback write warning: {e}")
        
        return {
            "success": True,
            "filename": file.filename,
            "document_type": doc_type,
            "confidence": confidence,
            "extracted_data": extracted_json,
            "raw_text": cleaned[:500],  
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
