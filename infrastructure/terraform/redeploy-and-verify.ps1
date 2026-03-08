param(
  [switch]$SkipApply,
  [int]$MaxAttempts = 30,
  [int]$SleepSeconds = 20
)

$ErrorActionPreference = "Stop"
$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptRoot

function Resolve-TerraformExe {
  $cmd = Get-Command terraform -ErrorAction SilentlyContinue
  if ($cmd) {
    return $cmd.Source
  }

  $localExe = Join-Path $ScriptRoot ".bin\terraform.exe"
  if (Test-Path $localExe) {
    return $localExe
  }

  throw "Terraform 未找到，请先安装 Terraform 或使用仓库内 .bin\terraform.exe"
}

function Invoke-Checked {
  param(
    [string]$Exe,
    [string[]]$CmdArgs
  )

  & $Exe @CmdArgs
  if ($LASTEXITCODE -ne 0) {
    throw "Command failed: $Exe $($CmdArgs -join ' ')"
  }
}

function Resolve-PublicKeyContent {
  if ($env:TF_VAR_public_key_content -and $env:TF_VAR_public_key_content.Trim() -ne "") {
    return $env:TF_VAR_public_key_content.Trim()
  }

  $repoKey = Join-Path $ScriptRoot "github_deploy_key.pub"
  if (Test-Path $repoKey) {
    return (Get-Content -Raw $repoKey).Trim()
  }

  $candidates = @(
    (Join-Path $HOME ".ssh\id_ed25519.pub"),
    (Join-Path $HOME ".ssh\id_rsa.pub")
  )

  foreach ($p in $candidates) {
    if (Test-Path $p) {
      return (Get-Content -Raw $p).Trim()
    }
  }

  throw "未找到可用公钥，请提供 TF_VAR_public_key_content 或创建 github_deploy_key.pub"
}

function Wait-Http200 {
  param(
    [string]$Url,
    [int]$Attempts,
    [int]$IntervalSeconds
  )

  for ($i = 1; $i -le $Attempts; $i++) {
    try {
      $resp = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 15
      if ($resp.StatusCode -eq 200) {
        Write-Host "[OK] $Url -> 200" -ForegroundColor Green
        return $true
      }
      Write-Host "[WAIT] $Url -> $($resp.StatusCode)" -ForegroundColor Yellow
    }
    catch {
      Write-Host "[WAIT] $Url -> $($_.Exception.Message)" -ForegroundColor Yellow
    }

    Start-Sleep -Seconds $IntervalSeconds
  }

  return $false
}

function Get-LoginToken {
  param(
    [string]$BaseUrl,
    [string]$UserName,
    [string]$Password
  )

  try {
    $resp = Invoke-WebRequest -Uri "$BaseUrl/api/sys/login/" -Method Post -Body @{ userName = $UserName; passWord = $Password } -UseBasicParsing -TimeoutSec 20
    $obj = $resp.Content | ConvertFrom-Json
    return $obj.data.token
  }
  catch {
    return $null
  }
}

$setEnvPath = Join-Path $ScriptRoot "set-env.ps1"
if (Test-Path $setEnvPath) {
  . $setEnvPath
}

if (-not $env:AWS_ACCESS_KEY_ID -or -not $env:AWS_SECRET_ACCESS_KEY) {
  throw "AWS 凭证未配置，请先执行 set-env.ps1 或设置 AWS_* 环境变量"
}

$TerraformExe = Resolve-TerraformExe
$env:TF_VAR_public_key_content = Resolve-PublicKeyContent

if (-not $env:TF_VAR_db_password -or $env:TF_VAR_db_password.Trim() -eq "") {
  $env:TF_VAR_db_password = "Exam123456!"
}
if (-not $env:TF_VAR_key_pair_name -or $env:TF_VAR_key_pair_name.Trim() -eq "") {
  $env:TF_VAR_key_pair_name = "fyp-keypair"
}

$env:AWS_PAGER = ""

Write-Host "=== 1) terraform init ===" -ForegroundColor Cyan
Invoke-Checked -Exe $TerraformExe -CmdArgs @("init")

Write-Host "=== 2) terraform validate ===" -ForegroundColor Cyan
Invoke-Checked -Exe $TerraformExe -CmdArgs @("validate")

Write-Host "=== 3) terraform plan ===" -ForegroundColor Cyan
Invoke-Checked -Exe $TerraformExe -CmdArgs @("plan", "-out=tfplan", "-input=false")

if (-not $SkipApply) {
  Write-Host "=== 4) terraform apply ===" -ForegroundColor Cyan
  Invoke-Checked -Exe $TerraformExe -CmdArgs @("apply", "-auto-approve", "tfplan")
}
else {
  Write-Host "[SkipApply] apply skipped; only outputs and checks will run." -ForegroundColor Yellow
}

Write-Host "=== 5) Read outputs ===" -ForegroundColor Cyan
$frontendUrl = & $TerraformExe output -raw frontend_url
$backendUrl = & $TerraformExe output -raw backend_api_url

Write-Host "frontend: $frontendUrl"
Write-Host "backend : $backendUrl"

$healthUrl = $frontendUrl.TrimEnd("/") + "/api/health/simple/"
Write-Host "=== 6) Health check ===" -ForegroundColor Cyan
$frontOk = Wait-Http200 -Url $frontendUrl -Attempts $MaxAttempts -IntervalSeconds $SleepSeconds
$apiOk = Wait-Http200 -Url $healthUrl -Attempts $MaxAttempts -IntervalSeconds $SleepSeconds

if (-not ($frontOk -and $apiOk)) {
  throw "Service not ready in expected time: frontOk=$frontOk apiOk=$apiOk"
}

Write-Host "=== 7) Role login check ===" -ForegroundColor Cyan
$base = $frontendUrl.TrimEnd("/")
$admin = Get-LoginToken -BaseUrl $base -UserName "admin" -Password "123456"
$teacher = Get-LoginToken -BaseUrl $base -UserName "teacher" -Password "123456"
$student = Get-LoginToken -BaseUrl $base -UserName "student" -Password "123456"

if (-not $admin) {
  throw "Admin login failed: admin/123456"
}
if (-not $teacher) {
  throw "Teacher login failed: teacher/123456"
}
if (-not $student) {
  throw "Student login failed: student/123456"
}

Write-Host "[OK] admin/teacher/student login all successful" -ForegroundColor Green
Write-Host "=== Done ===" -ForegroundColor Green
Write-Host "Redeploy and verification passed. Run destroy after demo to save cost." -ForegroundColor Green
