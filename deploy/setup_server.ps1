<#
Intelligent Exam System - Windows PowerShell one-click setup

Prereqs:
- Windows Server 2019/2022 (or Windows 10+)
- Python 3.10+ in PATH (py -3)
- Node.js 16/18+ in PATH
- MySQL Server reachable
- (Optional) IIS or Nginx for reverse proxy; script uses Uvicorn directly

Usage (as Administrator PowerShell):
  powershell -ExecutionPolicy Bypass -File deploy\setup_server.ps1 -ProjectRoot "C:\FYP2025-main" -EnvFile "C:\exam\.env" -DBImport Yes
#>

param(
  [Parameter(Mandatory=$true)] [string]$ProjectRoot,
  [Parameter(Mandatory=$false)] [string]$EnvFile = "C:\\exam\\.env",
  [Parameter(Mandatory=$false)] [ValidateSet('Yes','No')] [string]$DBImport = 'No',
  [Parameter(Mandatory=$false)] [int]$Port = 8000
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Ensure-Directory($Path) {
  if (-not (Test-Path $Path)) { New-Item -ItemType Directory -Force -Path $Path | Out-Null }
}

Write-Host "[1/7] Ensuring env file at $EnvFile ..."
Ensure-Directory (Split-Path -Parent $EnvFile)
if (-not (Test-Path $EnvFile)) {
  Copy-Item -Force (Join-Path $ProjectRoot 'env.example') $EnvFile
  Write-Host "INFO: Created $EnvFile from env.example. Please edit secrets inside it."
}

Write-Host "[2/7] Backend setup (venv, requirements, migrate/collectstatic)..."
Push-Location (Join-Path $ProjectRoot 'source\server')
py -3 -m venv .venv
& .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip wheel
pip install -r requirements.txt uvicorn gunicorn

# Attempt mysqlclient import; fallback to PyMySQL
python - << 'PY'
try:
    import MySQLdb  # noqa: F401
    print('mysqlclient available')
except Exception:
    print('mysqlclient missing, installing PyMySQL fallback...')
    import subprocess, sys
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pymysql'])
    init_path = 'server/__init__.py'
    try:
        with open(init_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        content = ''
    if 'pymysql.install_as_MySQLdb()' not in content:
        with open(init_path, 'a', encoding='utf-8') as f:
            f.write('\nimport pymysql\npymysql.install_as_MySQLdb()\n')
PY

if ($DBImport -eq 'Yes') {
  Write-Host "[2.1] Importing MySQL schema and sample data..."
  & mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS db_exam CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
  & mysql -u root -p db_exam < (Join-Path $ProjectRoot 'database\db_exam.sql')
  $practice = Join-Path $ProjectRoot 'database\init_practice_data.sql'
  if (Test-Path $practice) { & mysql -u root -p db_exam < $practice }
} else {
  Write-Host "[2.1] Skipping DB import; running Django migrations instead..."
  python manage.py migrate --noinput
}

python manage.py collectstatic --noinput
Pop-Location

Write-Host "[3/7] Frontend build (Vue)..."
Push-Location (Join-Path $ProjectRoot 'source\client')
if (Test-Path 'package-lock.json') { npm ci } else { npm install }
npm run build
Pop-Location

Write-Host "[4/7] Creating Windows service (NSSM) for Uvicorn (optional)..."
try {
  if (-not (Get-Command nssm -ErrorAction SilentlyContinue)) {
    Write-Host "NSSM not found; skipping service installation. You can install NSSM and re-run."
  } else {
    $AppDir = Join-Path $ProjectRoot 'source\server'
    $PythonExe = Join-Path $AppDir '.venv\Scripts\python.exe'
    nssm install ExamUvicorn $PythonExe
    nssm set ExamUvicorn AppDirectory $AppDir
    nssm set ExamUvicorn AppParameters "-m uvicorn server.asgi:application --host 0.0.0.0 --port $Port --workers 2"
    nssm set ExamUvicorn Start SERVICE_AUTO_START
    nssm start ExamUvicorn
  }
} catch {
  Write-Host "Skipping service creation due to error: $_"
}

Write-Host "[5/7] Quick run command (manual):"
Write-Host "`n  cd $ProjectRoot\source\server"
Write-Host "   .\.venv\Scripts\Activate.ps1"
Write-Host "   python -m uvicorn server.asgi:application --host 0.0.0.0 --port $Port --workers 2`n"

Write-Host "[6/7] Notes: Configure a reverse proxy (IIS ARR or Nginx on Windows) to serve the built frontend from source\\client\\dist and proxy /api/ to http://127.0.0.1:$Port/api/"

Write-Host "[7/7] Done. Edit env at: $EnvFile"


