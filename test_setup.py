"""
Test script to verify the Document Intelligence System setup.
Run this to check if everything is working correctly.
"""
import sys
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed."""
    print("🔍 Checking dependencies...")
    required = ['fastapi', 'uvicorn', 'pytesseract', 'easyocr', 'sklearn', 'PIL']
    missing = []
    
    for package in required:
        try:
            if package == 'PIL':
                import PIL
            elif package == 'sklearn':
                import sklearn
            else:
                __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - NOT INSTALLED")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("   Run: pip install -r requirementss.txt")
        return False
    return True

def check_model():
    """Check if classifier model exists."""
    print("\n🤖 Checking ML model...")
    model_path = Path("app/model_artifacts/classifier.pkl")
    
    if model_path.exists():
        print(f"  ✅ Model found at {model_path}")
        return True
    else:
        print(f"  ❌ Model not found at {model_path}")
        print("   Run: python app/train_classifier.py")
        return False

def check_tesseract():
    """Check if Tesseract OCR is installed."""
    print("\n📸 Checking Tesseract OCR...")
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print(f"  ✅ Tesseract {version} found")
        return True
    except Exception as e:
        print(f"  ❌ Tesseract not found or not in PATH")
        print(f"     Error: {e}")
        print("   Install from: https://github.com/UB-Mannheim/tesseract/wiki")
        return False

def check_config():
    """Check configuration files."""
    print("\n⚙️  Checking configuration...")
    
    config_file = Path("app/config.py")
    if config_file.exists() and config_file.stat().st_size > 0:
        print(f"  ✅ config.py exists")
    else:
        print(f"  ❌ config.py is missing or empty")
        return False
    
    env_example = Path(".env.example")
    if env_example.exists():
        print(f"  ✅ .env.example exists")
    
    return True

def check_frontend():
    """Check if frontend files exist."""
    print("\n🎨 Checking frontend...")
    
    frontend_file = Path("frontend/index.html")
    if frontend_file.exists():
        print(f"  ✅ Frontend found at frontend/index.html")
        return True
    else:
        print(f"  ❌ Frontend not found")
        return False

def test_api_import():
    """Test if API can be imported."""
    print("\n🚀 Testing API import...")
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        import main_standalone
        print(f"  ✅ API module imported successfully")
        return True
    except Exception as e:
        print(f"  ❌ Failed to import API: {e}")
        return False

def main():
    """Run all checks."""
    print("=" * 60)
    print("  Document Intelligence System - Setup Verification")
    print("=" * 60)
    print()
    
    checks = [
        check_dependencies(),
        check_tesseract(),
        check_model(),
        check_config(),
        check_frontend(),
        test_api_import()
    ]
    
    print("\n" + "=" * 60)
    if all(checks):
        print("✅ All checks passed! System is ready to use.")
        print("\nTo start the system:")
        print("  1. Run: uvicorn main_standalone:app --reload")
        print("  2. Open: frontend/index.html in your browser")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print("\nQuick fix commands:")
        print("  pip install -r requirementss.txt")
        print("  python app/train_classifier.py")
    print("=" * 60)

if __name__ == "__main__":
    main()
