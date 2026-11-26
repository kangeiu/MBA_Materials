$ErrorActionPreference = "Stop"

Write-Host "=== 1. Cap quyen chay script & cai dat uv ===" -ForegroundColor Cyan
try {
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force -ErrorAction SilentlyContinue
} catch {
    # Bo qua neu dang bi ghi de boi Process/Machine Policy (vi du: -ExecutionPolicy Bypass)
}

powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User") + ";$HOME\.local\bin;$HOME\.cargo\bin"

Write-Host "=== 2. Cai dat Python 3.12 ===" -ForegroundColor Cyan
uv python install 3.12

Write-Host "=== 3. Khoi tao du an & moi truong ao (.venv) ===" -ForegroundColor Cyan
$projDir = "$HOME\Downloads\code-practice"
New-Item -ItemType Directory -Force -Path $projDir | Out-Null
Set-Location $projDir

if (-not (Test-Path "pyproject.toml")) {
    uv init --bare --python 3.12
}

uv venv --python 3.12 --clear
.\.venv\Scripts\Activate.ps1

Write-Host "=== 4. Tao requirements.txt & cai dat thu vien ===" -ForegroundColor Cyan
@(
    "numpy"
    "pandas"
    "matplotlib"
    "seaborn"
    "streamlit"
    "yfinance"
) | Set-Content -Encoding Ascii requirements.txt

uv pip install -r requirements.txt

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "HOAN TAT CAI DAT!" -ForegroundColor Green
Write-Host "Thu muc du an: $projDir" -ForegroundColor Green
Write-Host "Python version: $(python --version)" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
