# 🤖 AI Document Intelligence System

A production-ready AI system for **OCR**, **document classification**, and **intelligent data extraction** with a modern web interface.

## 🎯 Features

- **✅ OCR Processing**: Tesseract + EasyOCR for reliable text extraction
- **✅ AI Classification**: Automatically identifies document types (Invoice, CV, ID Card, Receipt)
- **✅ Smart Extraction**: Extracts key fields based on document type
- **✅ REST API**: FastAPI backend with comprehensive error handling
- **✅ Modern Frontend**: Clean, responsive UI with drag-and-drop upload
- **✅ Database Support**: PostgreSQL + Supabase integration
- **✅ Real-time Processing**: Fast document analysis pipeline

## 📊 Document Types & Extracted Fields

| Document Type | Extracted Information |
|--------------|----------------------|
| **Invoice** | Total, Tax, Company, Date, Invoice Number |
| **CV/Resume** | Skills, Experience, Technologies, Education |
| **ID Card** | Name, Date of Birth, Address, ID Number |
| **Receipt** | Store, Total, Date, Items |

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Tesseract OCR installed on your system

#### Install Tesseract:

**Windows:**
```powershell
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Or use chocolatey:
choco install tesseract
```

**Mac:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

### Installation

1. **Clone and setup:**
```powershell
cd e:\doc_intelligence
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirementss.txt
```

2. **Train the ML classifier:**
```powershell
python app/train_classifier.py
```

3. **Configure environment (optional):**
```powershell
cp .env.example .env
# Edit .env with your settings (Supabase is optional)
```

4. **Start the backend API:**
```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. **Open the frontend:**
   - Open `frontend/index.html` in your browser
   - Or serve it: `python -m http.server 3000 --directory frontend`

## 📁 Project Structure

```
doc_intelligence/
├── app/
│   ├── main.py              # FastAPI application
│   ├── ocr.py               # OCR processing (Tesseract + EasyOCR)
│   ├── classifier.py        # ML document classifier
│   ├── extractor.py         # Field extraction logic
│   ├── text_processor.py    # Text cleaning
│   ├── database.py          # Database models (SQLAlchemy)
│   ├── schemas.py           # Pydantic schemas
│   ├── config.py            # Configuration management
│   ├── train_classifier.py  # Train ML model
│   └── model_artifacts/     # Trained ML models
│       └── classifier.pkl
├── frontend/
│   └── index.html           # Web UI (HTML + CSS + JS)
├── requirementss.txt        # Python dependencies
├── .env.example             # Environment template
└── README.md                # This file
```

## 🔧 API Endpoints

### `POST /process`
Upload and process a document.

**Request:**
```bash
curl -X POST "http://localhost:8000/process" \
  -F "file=@invoice.pdf"
```

**Response:**
```json
{
  "success": true,
  "filename": "invoice.pdf",
  "document_type": "invoice",
  "confidence": 0.95,
  "extracted_data": {
    "invoice_total": ["$1,500.00"],
    "invoice_date": ["01/15/2024"],
    "company": ["ABC Traders"]
  },
  "raw_text": "Invoice Number INV-001...",
  "file_url": "https://..."
}
```

### `GET /health`
Health check endpoint.

### `GET /`
API information.

## 🎨 Frontend Features

- **Drag & Drop Upload**: Easy file selection
- **Real-time Processing**: Visual feedback during processing
- **Beautiful Results**: Clean display of extracted data
- **Responsive Design**: Works on all devices
- **Error Handling**: User-friendly error messages

## 🧪 Testing the System

1. **Test with sample documents:**
   - Create test invoices, CVs, or ID cards
   - Upload through the web interface
   - Verify extracted fields

2. **API testing:**
```powershell
# Using PowerShell
$file = Get-Item "test_invoice.pdf"
$form = @{ file = $file }
Invoke-RestMethod -Uri "http://localhost:8000/process" -Method Post -Form $form
```

## 📦 Dependencies

Core libraries:
- `fastapi` - Modern web framework
- `pytesseract` - Tesseract OCR wrapper
- `easyocr` - Deep learning OCR
- `scikit-learn` - ML classifier
- `supabase` - Cloud storage (optional)
- `sqlalchemy` - Database ORM
- `pillow` - Image processing

## 🔐 Configuration

The system supports multiple configurations:

1. **Standalone mode**: Works without Supabase (local processing only)
2. **Supabase mode**: Cloud storage + database
3. **PostgreSQL mode**: Local database with SQLAlchemy

Edit `.env` to configure your setup.

## 🛠️ Customization

### Add New Document Types

1. **Update training data** in `train_classifier.py`
2. **Add extraction logic** in `extractor.py`:
```python
def extract_passport(text):
    return {
        "passport_number": re.findall(r"[A-Z]{2}\d{7}", text),
        "expiry_date": re.findall(r"Expiry: (\d{2}/\d{2}/\d{4})", text)
    }
```
3. **Retrain model**: `python app/train_classifier.py`

### Improve OCR Accuracy

- Use higher quality scans
- Pre-process images (deskew, denoise)
- Try different OCR engines (Google Vision, Azure OCR)

## 🚨 Troubleshooting

**Issue: "Classifier model not found"**
```powershell
python app/train_classifier.py
```

**Issue: "Tesseract not found"**
- Install Tesseract and add to PATH
- Or set path: `pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'`

**Issue: CORS errors**
- Backend allows all origins by default
- For production, update CORS settings in `main.py`

## 📈 Performance

- Average processing time: 2-5 seconds per document
- Supports files up to 10MB
- Handles multiple document types
- Confidence scores for classification

## 🌟 Real-World Applications

- **Accounting**: Automated invoice processing
- **HR**: Resume parsing and skill extraction
- **Compliance**: ID verification and data extraction
- **Retail**: Receipt digitization
- **Healthcare**: Form processing

## 📄 License

This is an educational/demo project. Customize as needed for your use case.

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional document types
- Better extraction patterns
- UI enhancements
- Performance optimization
- Test coverage

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the code comments
3. Test with sample documents first

---

**Built with ❤️ using FastAPI, Tesseract, EasyOCR, and Modern Web Technologies**
