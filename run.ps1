# Start Enterprise RAG API (uses project venv — no manual activation required)
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

$Python = Join-Path $ProjectRoot "venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    Write-Error "Virtual environment not found. Run: python -m venv venv; .\venv\Scripts\pip install -r requirements.txt"
    exit 1
}

& $Python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
