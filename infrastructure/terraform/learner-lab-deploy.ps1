param(
  [switch]$PlanOnly,
  [switch]$SkipRollback,
  [int]$MaxHealthChecks = 12,
  [int]$HealthIntervalSec = 20
)

$ErrorActionPreference = 'Stop'
$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptRoot

function Get-TerraformExe {
  $cmd = Get-Command terraform -ErrorAction SilentlyContinue
  if ($cmd) { return $cmd.Source }
  $local = Join-Path $ScriptRoot '.bin\terraform.exe'
  if (Test-Path $local) { return $local }
  throw 'Terraform not found. Please install Terraform or provide infrastructure/terraform/.bin/terraform.exe'
}

function Invoke-TF {
  param(
    [string]$TerraformExe,
    [string[]]$CommandArgs
  )
  $tfOutput = & $TerraformExe @CommandArgs 2>&1
  if ($tfOutput) {
    $tfOutput | ForEach-Object { $_ }
  }

  if ($LASTEXITCODE -ne 0) {
    $joined = ($tfOutput | Out-String)
    if ($joined -match 'UnauthorizedOperation' -or $joined -match 'voc-cancel-cred') {
      throw @"
Terraform 命令失败：terraform $($CommandArgs -join ' ')

检测到 AWS Academy/Learner Lab 权限被拒绝（voc-cancel-cred / UnauthorizedOperation）。
这通常是 Lab 会话过期或凭证被撤销导致，不是 Terraform 配置语法问题。

请先在 Learner Lab 重新启动会话并更新临时凭证，然后重试：
1) 重新打开/启动 AWS Academy Learner Lab
2) 重新执行 set-env.ps1（或更新 AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY / AWS_SESSION_TOKEN）
3) 运行 .\\learner-lab-deploy.ps1
"@
    }
    throw "Terraform command failed: terraform $($CommandArgs -join ' ')"
  }
}

function Resolve-PublicKeyContent {
  $deployPub = Join-Path $ScriptRoot 'github_deploy_key.pub'
  if (Test-Path $deployPub) {
    return (Get-Content -Raw $deployPub).Trim()
  }

  $candidates = @(
    (Join-Path $HOME '.ssh\id_rsa.pub'),
    (Join-Path $HOME '.ssh\id_ed25519.pub')
  )

  foreach ($p in $candidates) {
    if (Test-Path $p) {
      return (Get-Content -Raw $p).Trim()
    }
  }

  throw 'No public key found. Please create github_deploy_key.pub or ~/.ssh/id_rsa.pub'
}

function Try-SetDeployKeyPrivate {
  $deployPriv = Join-Path $ScriptRoot 'github_deploy_key'
  if (Test-Path $deployPriv) {
    $env:TF_VAR_github_deploy_key_private = Get-Content -Raw $deployPriv
    Write-Host 'Using github_deploy_key for private repo clone.' -ForegroundColor Cyan
  } else {
    Write-Warning 'github_deploy_key not found. Will rely on public repo URL or existing TF_VAR_github_deploy_key_private.'
  }
}

function Test-ServiceReady {
  param(
    [string]$FrontendUrl,
    [int]$Checks,
    [int]$IntervalSec
  )

  $healthUrl = $FrontendUrl.TrimEnd('/') + '/api/health/simple/'

  for ($i = 1; $i -le $Checks; $i++) {
    Write-Host "Health check $i/$Checks" -ForegroundColor Cyan
    $frontOk = $false
    $apiOk = $false

    try {
      $f = Invoke-WebRequest -Uri $FrontendUrl -UseBasicParsing -TimeoutSec 15
      if ($f.StatusCode -eq 200) { $frontOk = $true }
      Write-Host "Frontend status: $($f.StatusCode)" -ForegroundColor DarkGray
    } catch {
      Write-Warning "Frontend check failed: $($_.Exception.Message)"
    }

    try {
      $a = Invoke-WebRequest -Uri $healthUrl -UseBasicParsing -TimeoutSec 15
      if ($a.StatusCode -eq 200) { $apiOk = $true }
      Write-Host "API status: $($a.StatusCode)" -ForegroundColor DarkGray
    } catch {
      Write-Warning "API check failed: $($_.Exception.Message)"
    }

    if ($frontOk -and $apiOk) {
      return $true
    }

    Start-Sleep -Seconds $IntervalSec
  }

  return $false
}

$setEnv = Join-Path $ScriptRoot 'set-env.ps1'
if (Test-Path $setEnv) {
  & $setEnv
}

if (-not $env:AWS_ACCESS_KEY_ID -or -not $env:AWS_SECRET_ACCESS_KEY) {
  throw 'AWS credentials missing. Run set-env.ps1 first.'
}

$terraform = Get-TerraformExe
$env:TF_VAR_public_key_content = Resolve-PublicKeyContent
Try-SetDeployKeyPrivate

if (-not $env:TF_VAR_db_password -or $env:TF_VAR_db_password.Trim() -eq '') {
  $env:TF_VAR_db_password = 'Exam123456!'
}

if (-not $env:TF_VAR_key_pair_name -or $env:TF_VAR_key_pair_name.Trim() -eq '') {
  $env:TF_VAR_key_pair_name = 'fyp-keypair'
}

Write-Host 'Step 1/5: terraform init' -ForegroundColor Green
Invoke-TF -TerraformExe $terraform -CommandArgs @('init')

Write-Host 'Step 2/5: terraform validate' -ForegroundColor Green
Invoke-TF -TerraformExe $terraform -CommandArgs @('validate')

Write-Host 'Step 3/5: terraform plan (HA)' -ForegroundColor Green
Invoke-TF -TerraformExe $terraform -CommandArgs @('plan', '-input=false', '-var=enable_ha=true', '-out=tfplan')

if ($PlanOnly) {
  Write-Host 'PlanOnly mode complete. No resources applied.' -ForegroundColor Yellow
  exit 0
}

Write-Host 'Step 4/5: terraform apply' -ForegroundColor Green
Invoke-TF -TerraformExe $terraform -CommandArgs @('apply', '-auto-approve', 'tfplan')

$frontend = & $terraform output -raw frontend_url
$api = & $terraform output -raw backend_api_url
Write-Host "Frontend URL: $frontend" -ForegroundColor Cyan
Write-Host "API URL: $api" -ForegroundColor Cyan

Write-Host 'Step 5/5: health checks' -ForegroundColor Green
$ok = Test-ServiceReady -FrontendUrl $frontend -Checks $MaxHealthChecks -IntervalSec $HealthIntervalSec

if ($ok) {
  Write-Host 'Deployment succeeded and both frontend/API are reachable.' -ForegroundColor Green
  exit 0
}

Write-Warning 'Deployment completed but health checks did not pass in time.'
if (-not $SkipRollback) {
  Write-Warning 'Auto rollback enabled: running terraform destroy...'
  Invoke-TF -TerraformExe $terraform -CommandArgs @('destroy', '-auto-approve', '-input=false', '-var=enable_ha=true')
  throw 'Health checks failed; resources were rolled back automatically.'
}

throw 'Health checks failed. Resources are kept because -SkipRollback was specified.'
