# Start Document Intelligence System
Write-Host ' Starting Document Intelligence System...' -ForegroundColor Cyan
Write-Host ''

# Activate virtual environment
Write-Host ' Activating virtual environment...' -ForegroundColor Cyan
& '.\venv\Scripts\Activate.ps1'

# Check if dependencies are installed
$pipList = pip list
if ($pipList -notmatch 'fastapi') {
    Write-Host ' Installing dependencies...' -ForegroundColor Yellow
    pip install -r requirements.txt
    Write-Host ' Dependencies installed.' -ForegroundColor Green
}

Write-Host ''
Write-Host '=====================================' -ForegroundColor Cyan
Write-Host '  Document Intelligence API Server  ' -ForegroundColor Cyan
Write-Host '=====================================' -ForegroundColor Cyan
Write-Host ''
Write-Host ' Backend API: http://localhost:8000' -ForegroundColor Green
Write-Host ' API Docs: http://localhost:8000/docs' -ForegroundColor Green
Write-Host ' Frontend: Open frontend\index.html in browser' -ForegroundColor Green
Write-Host ''
Write-Host 'Press Ctrl+C to stop the server' -ForegroundColor Yellow
Write-Host ''

# Start the server
uvicorn main_standalone:app --reload --host 0.0.0.0 --port 8000