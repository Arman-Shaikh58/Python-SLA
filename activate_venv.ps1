# activate_venv.ps1

# Path to the virtual environment (change if needed)
$venvPath = ".\venv\Scripts\Activate"

# Check if the virtual environment activation script exists
if (-Not (Test-Path $venvPath)) {
    Write-Host "❌ Virtual environment activation script not found at $venvPath"
    exit 1
}
$cdcmd="cd SLA"
$startservercmd="python manage.py runserver"
Write-Host "🚀 Activating virtual environment..."
. $venvPath

# Execute the commands
Invoke-Expression $cdcmd
Invoke-Expression $startservercmd

Write-Host "🚀 Virtual environment activated and server started"


