import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/doc_intelligence")

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "documents")

# Model Configuration
CLASSIFIER_MODEL_PATH = os.getenv("CLASSIFIER_MODEL_PATH", "app/model_artifacts/classifier.pkl")

# API Configuration
UPLOAD_MAX_SIZE = int(os.getenv("UPLOAD_MAX_SIZE", 10 * 1024 * 1024))  # 10MB default
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp"}
