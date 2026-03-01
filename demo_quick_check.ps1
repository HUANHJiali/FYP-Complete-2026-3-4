param(
    [string]$RootPath = "D:\fyp-2026-2-8-master\fyp-2026-2-8-master"
)

$ErrorActionPreference = "Stop"

function Write-Step($text) {
    Write-Host "`n=== $text ===" -ForegroundColor Cyan
}

Set-Location $RootPath

Write-Step "1) Check Docker containers"
docker ps --format "table {{.Names}}`t{{.Status}}"

Write-Step "2) Run full feature smoke"
python feature_smoke_check_20260301.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Smoke check failed. Please fix issues before demo." -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Step "3) Run exam flow regression (submit/status/publish)"
docker exec fyp_backend python manage.py test app.tests.test_student_exam_flow app.tests.test_lifecycle_status_fields --verbosity 1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Exam flow regression failed. Please fix issues before demo." -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Step "4) Demo readiness complete"
Write-Host "All checks passed. Ready for demo." -ForegroundColor Green
Write-Host "Report file: FEATURE_SMOKE_REPORT_20260301.md" -ForegroundColor Green
