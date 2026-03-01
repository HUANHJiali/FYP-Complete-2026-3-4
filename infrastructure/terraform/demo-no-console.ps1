param(
  [switch]$SkipApply,
  [switch]$SkipDestroy,
  [switch]$ShowHaFailover
)

$ErrorActionPreference = 'Stop'
$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$TerraformExe = $null
$AwsExe = $null

Set-Location $ScriptRoot

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

function Require-Command {
  param([string]$Name)
  if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
    throw "Command not found: $Name"
  }
}

function Resolve-AwsExe {
  $cmd = Get-Command aws -ErrorAction SilentlyContinue
  if ($cmd) {
    return $cmd.Source
  }
  $default = 'C:\Program Files\Amazon\AWSCLIV2\aws.exe'
  if (Test-Path $default) {
    return $default
  }
  throw 'AWS CLI not found. Install AWS CLI or verify C:\Program Files\Amazon\AWSCLIV2\aws.exe exists.'
}

function Resolve-TerraformExe {
  $cmd = Get-Command terraform -ErrorAction SilentlyContinue
  if ($cmd) {
    return $cmd.Source
  }

  $localBin = Join-Path $ScriptRoot '.bin'
  $localExe = Join-Path $localBin 'terraform.exe'
  if (Test-Path $localExe) {
    return $localExe
  }

  Write-Host 'Terraform not found. Downloading local binary...' -ForegroundColor Yellow
  New-Item -ItemType Directory -Force -Path $localBin | Out-Null
  $zipPath = Join-Path $localBin 'terraform_1.14.6_windows_amd64.zip'
  Invoke-WebRequest -Uri 'https://releases.hashicorp.com/terraform/1.14.6/terraform_1.14.6_windows_amd64.zip' -OutFile $zipPath
  Expand-Archive -Path $zipPath -DestinationPath $localBin -Force

  if (-not (Test-Path $localExe)) {
    throw 'Terraform auto-download failed. Please check network and retry.'
  }

  return $localExe
}

function Resolve-PublicKeyContent {
  if ($env:TF_VAR_public_key_content -and $env:TF_VAR_public_key_content.Trim() -ne '') {
    return $env:TF_VAR_public_key_content
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

  $sshKeygen = Get-Command ssh-keygen -ErrorAction SilentlyContinue
  if ($sshKeygen) {
    $genPath = Join-Path $ScriptRoot '.tmp_fyp_key'
    if (-not (Test-Path ($genPath + '.pub'))) {
      & $sshKeygen.Source -t rsa -b 2048 -f $genPath -N '' -q
      if ($LASTEXITCODE -ne 0) {
        throw 'ssh-keygen failed while creating temporary key pair.'
      }
    }
    return (Get-Content -Raw ($genPath + '.pub')).Trim()
  }

  throw 'No SSH public key found. Create ~/.ssh/id_rsa.pub or set TF_VAR_public_key_content.'
}

$TerraformExe = Resolve-TerraformExe
$AwsExe = Resolve-AwsExe
$env:TF_VAR_public_key_content = Resolve-PublicKeyContent
if (-not $env:TF_VAR_key_pair_name -or $env:TF_VAR_key_pair_name.Trim() -eq '') {
  $env:TF_VAR_key_pair_name = 'fyp-keypair-demo'
}
if (-not $env:TF_VAR_db_password -or $env:TF_VAR_db_password.Trim() -eq '') {
  $env:TF_VAR_db_password = 'Exam123456!'
}

if (-not $env:AWS_ACCESS_KEY_ID -or -not $env:AWS_SECRET_ACCESS_KEY) {
  throw "AWS credentials not set. Run set-env.ps1 or set AWS_* environment variables first."
}

Write-Host "=== Step 1/8: Verify AWS credentials ===" -ForegroundColor Cyan
Invoke-Checked -Exe $AwsExe -CmdArgs @('sts', 'get-caller-identity')

Write-Host "=== Step 2/8: Terraform init ===" -ForegroundColor Cyan
Invoke-Checked -Exe $TerraformExe -CmdArgs @('init')

Write-Host "=== Step 3/8: Terraform validate ===" -ForegroundColor Cyan
Invoke-Checked -Exe $TerraformExe -CmdArgs @('validate')

Write-Host "=== Step 4/8: Terraform plan (HA enabled) ===" -ForegroundColor Cyan
Invoke-Checked -Exe $TerraformExe -CmdArgs @('plan', '-var=enable_ha=true', '-out=tfplan', '-input=false')

if (-not $SkipApply) {
  Write-Host "=== Step 5/8: Terraform apply ===" -ForegroundColor Cyan
  Invoke-Checked -Exe $TerraformExe -CmdArgs @('apply', '-auto-approve', 'tfplan')
} else {
  Write-Host "Skip apply (SkipApply)" -ForegroundColor Yellow
}

if ($SkipApply) {
  Write-Host "Apply skipped, so outputs/health checks are skipped as well." -ForegroundColor Yellow
  if (-not $SkipDestroy) {
    Write-Host "=== Step 8/8: Terraform destroy ===" -ForegroundColor Cyan
    Invoke-Checked -Exe $TerraformExe -CmdArgs @('destroy', '-auto-approve', '-var=enable_ha=true', '-input=false')
  } else {
    Write-Host "Skip destroy (SkipDestroy)" -ForegroundColor Yellow
  }
  Write-Host "CLI demo finished." -ForegroundColor Green
  return
}

Write-Host "=== Step 6/8: Print key outputs ===" -ForegroundColor Cyan
$lb = & $TerraformExe output -raw load_balancer_dns
$frontend = & $TerraformExe output -raw frontend_url
$api = & $TerraformExe output -raw backend_api_url
$instanceIds = (& $TerraformExe output -json backend_instance_ids) | ConvertFrom-Json

Write-Host "ALB DNS: $lb"
Write-Host "Frontend URL: $frontend"
Write-Host "Backend API URL: $api"
Write-Host "Instance IDs: $($instanceIds -join ', ')"

Write-Host "=== Step 7/8: CLI health checks ===" -ForegroundColor Cyan
$maxAttempts = 30
$sleepSeconds = 20
$ready = $false
for ($attempt = 1; $attempt -le $maxAttempts; $attempt++) {
  Write-Host "Health attempt $attempt/$maxAttempts"
  $frontendOk = $false
  $apiOk = $false

  try {
    $frontendResp = Invoke-WebRequest -Uri $frontend -UseBasicParsing -TimeoutSec 20
    Write-Host "Frontend reachable, status: $($frontendResp.StatusCode)"
    if ($frontendResp.StatusCode -eq 200) {
      $frontendOk = $true
    }
  } catch {
    Write-Warning "Frontend check failed: $($_.Exception.Message)"
  }

  try {
    $healthResp = Invoke-WebRequest -Uri ($frontend.TrimEnd('/') + '/api/health/simple/') -UseBasicParsing -TimeoutSec 20
    Write-Host "API health check ok, status: $($healthResp.StatusCode)"
    if ($healthResp.StatusCode -eq 200) {
      $apiOk = $true
    }
  } catch {
    Write-Warning "API check failed: $($_.Exception.Message)"
  }

  if ($frontendOk -or $apiOk) {
    $ready = $true
    break
  }

  Start-Sleep -Seconds $sleepSeconds
}

if (-not $ready) {
  Write-Warning "Service is not ready after waiting. You can SSH to check /tmp/deploy.log and docker-compose logs."
}

if ($ShowHaFailover -and $instanceIds.Count -ge 2) {
  Write-Host "=== Optional: HA failover demo (CLI) ===" -ForegroundColor Cyan
  $target = $instanceIds[0]
  Write-Host "Stopping instance: $target"
  & $AwsExe ec2 stop-instances --instance-ids $target | Out-Null
  & $AwsExe ec2 wait instance-stopped --instance-ids $target
  Start-Sleep -Seconds 20
  try {
    $afterResp = Invoke-WebRequest -Uri $frontend -UseBasicParsing -TimeoutSec 20
    Write-Host "After failure, frontend still reachable, status: $($afterResp.StatusCode)"
  } catch {
    Write-Warning "Post-failover check failed: $($_.Exception.Message)"
  }
}

if (-not $SkipDestroy) {
  Write-Host "=== Step 8/8: Terraform destroy ===" -ForegroundColor Cyan
  Invoke-Checked -Exe $TerraformExe -CmdArgs @('destroy', '-auto-approve', '-var=enable_ha=true', '-input=false')
} else {
  Write-Host "Skip destroy (SkipDestroy)" -ForegroundColor Yellow
}

Write-Host "CLI demo finished." -ForegroundColor Green
