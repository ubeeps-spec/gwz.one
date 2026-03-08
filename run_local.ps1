Param(
  [string]$HostBind = "127.0.0.1",
  [int]$Port = 8000
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

# Resolve Python
$pyCmd = Get-Command py -ErrorAction SilentlyContinue
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if ($pyCmd) {
  $pyExe = $pyCmd.Source
  $pyArgs = @('-3')
} elseif ($pythonCmd) {
  $pyExe = $pythonCmd.Source
  $pyArgs = @()
} else {
  Write-Error "Python 3 not found. Please install Python 3 and add it to PATH."
  exit 1
}

# Ensure venv
$venvPy = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $venvPy)) {
  & $pyExe @pyArgs -m venv ".venv"
}

# Upgrade pip and install deps
& $venvPy -m pip install --upgrade pip
& $venvPy -m pip install -r "requirements.txt"

# Migrations
& $venvPy manage.py makemigrations
& $venvPy manage.py migrate

# Update site content
& $venvPy "scripts\update_content_zh.py"

# Start server (open browser after small delay)
$addr = "$($HostBind):$Port"
Start-Job -ScriptBlock { param($u) Start-Sleep -Seconds 2; Start-Process $u | Out-Null } -ArgumentList ("http://$($HostBind):$Port/") | Out-Null
& $venvPy manage.py runserver $addr
