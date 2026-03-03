param(
  [string]$Region = "us-east-1",
  [string]$AccountId = "386922361011",
  [string]$BackendTag = "latest",
  [string]$FrontendTag = "latest",
  [switch]$Destroy,
  [switch]$SkipBootstrap
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $repoRoot

$setEnv = Join-Path $repoRoot "infrastructure/terraform/set-env.ps1"
if (Test-Path $setEnv) {
  & $setEnv
}

$awsExe = "C:\Program Files\Amazon\AWSCLIV2\aws.exe"
if (-not (Test-Path $awsExe)) {
  throw "AWS CLI not found at C:\Program Files\Amazon\AWSCLIV2\aws.exe"
}

$dockerProxy = docker info --format "{{.HTTPProxy}} {{.HTTPSProxy}}" 2>$null
if ($dockerProxy -and $dockerProxy.Trim() -ne "") {
  Write-Warning "Detected Docker proxy: $dockerProxy"
  Write-Warning "If ECR login fails, check Docker Desktop -> Settings -> Resources -> Proxies."
}

& $awsExe sts get-caller-identity --region $Region --no-cli-pager | Out-Null

$registry = "$AccountId.dkr.ecr.$Region.amazonaws.com"
$backendUri = "$registry/fyp-backend:$BackendTag"
$frontendUri = "$registry/fyp-frontend:$FrontendTag"

$null = & $awsExe ecr describe-repositories --region $Region --repository-names fyp-backend --no-cli-pager 2>$null
if ($LASTEXITCODE -ne 0) {
  & $awsExe ecr create-repository --region $Region --repository-name fyp-backend --image-scanning-configuration scanOnPush=true --no-cli-pager | Out-Null
}

$null = & $awsExe ecr describe-repositories --region $Region --repository-names fyp-frontend --no-cli-pager 2>$null
if ($LASTEXITCODE -ne 0) {
  & $awsExe ecr create-repository --region $Region --repository-name fyp-frontend --image-scanning-configuration scanOnPush=true --no-cli-pager | Out-Null
}

$ecrPassword = (& $awsExe ecr get-login-password --region $Region --no-cli-pager).Trim()
docker login --username AWS --password $ecrPassword $registry

if ($Destroy) {
  Set-Location (Join-Path $repoRoot "infrastructure/cdk")
  npm install
  npx cdk destroy --force
  return
}

Write-Host "Build backend: $backendUri" -ForegroundColor Cyan
docker build -t $backendUri -f docker/backend/Dockerfile source/server
docker push $backendUri

Write-Host "Build frontend: $frontendUri" -ForegroundColor Cyan
docker build -t $frontendUri -f docker/frontend/Dockerfile.prod source/client
docker push $frontendUri

Set-Location (Join-Path $repoRoot "infrastructure/cdk")
npm install

if (-not $SkipBootstrap) {
  npx cdk bootstrap aws://$AccountId/$Region
  if ($LASTEXITCODE -ne 0) {
    throw @"
CDK bootstrap 失败。

在 AWS Academy Learner Lab 中，这通常是 IAM/CloudFormation 权限限制导致（例如无法创建或更新 CDKToolkit 相关资源）。
你可以：
1) 先重开 Lab 并刷新临时凭证后重试；
2) 或直接使用 Terraform 路径（infrastructure/terraform/learner-lab-deploy.ps1）。
3) 若已手动完成过 bootstrap，可加 -SkipBootstrap 仅执行 deploy。
"@
  }
}

npx cdk deploy --require-approval never -c backendImageUri=$backendUri -c frontendImageUri=$frontendUri -c dbName=db_exam
if ($LASTEXITCODE -ne 0) {
  throw "CDK deploy failed. If you are in Learner Lab, Terraform path is recommended."
}
