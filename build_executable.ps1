# Build Heliosylva as a standalone Windows app (dist\Heliosylva\Heliosylva.exe)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "Installing build dependencies..."
python -m pip install --upgrade pip
python -m pip install pygame numpy pyinstaller

Write-Host "Building executable (this may take a few minutes)..."
python -m PyInstaller Heliosylva.spec --noconfirm

$exe = Join-Path $PSScriptRoot "dist\Heliosylva\Heliosylva.exe"
if (Test-Path $exe) {
    Write-Host ""
    Write-Host "Success! Run the game with:"
    Write-Host "  $exe"
    Write-Host ""
    Write-Host "To share the game, zip or copy the entire folder:"
    Write-Host "  $(Join-Path $PSScriptRoot 'dist\Heliosylva')"
} else {
    Write-Error "Build finished but Heliosylva.exe was not found."
}
