Set-Location -Path "$PSScriptRoot\backend"
$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

if (Test-Path $python) {
    & $python -m uvicorn app.main:app --reload
} else {
    python -m uvicorn app.main:app --reload
}
