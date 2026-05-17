# Build Heliosylva as a single Windows .exe (all assets embedded).
# If scripts are blocked, use:  build_executable.bat
# Or one-time:  powershell -ExecutionPolicy Bypass -File .\build_executable.ps1
#
# Players download Heliosylva.exe and double-click — no zip, no install folder.

$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot



Write-Host "Installing build dependencies..."

python -m pip install --upgrade pip -q

python -m pip install pygame numpy pyinstaller -q



Write-Host "Verifying main.py..."

python -m py_compile main.py



Write-Host "Building single-file executable (may take several minutes)..."

python -m PyInstaller Heliosylva.spec --noconfirm --clean



$exe = Join-Path $PSScriptRoot "dist\Heliosylva.exe"

if (-not (Test-Path $exe)) {

    Write-Error "Build finished but dist\Heliosylva.exe was not found."

}



$exeMb = [math]::Round((Get-Item $exe).Length / 1MB, 1)

Write-Host ""

Write-Host "Success!"

Write-Host "  Ship this file:  $exe  ($exeMb MB)"

Write-Host ""

Write-Host "Players: download Heliosylva.exe, then double-click to play."

Write-Host "First launch may take a few seconds while Windows unpacks bundled assets."

Write-Host "If SmartScreen appears: More info -> Run anyway."

Write-Host ""

Write-Host "Optional: some hosts block .exe — zip only that file for upload:"

Write-Host ('  Compress-Archive -Path "' + $exe + '" -DestinationPath dist\Heliosylva-Windows.zip')

