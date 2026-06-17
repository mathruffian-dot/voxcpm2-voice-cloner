# repatch_xpu.ps1
# Re-apply Intel XPU device support patch to voxcpm after package upgrade.
# Usage: .\patches\repatch_xpu.ps1
#
# Logic:
#   1. Locate .venv voxcpm package file model/utils.py
#   2. If it already contains _has_xpu (patched) -> skip
#   3. If not patched -> backup original to patches\utils.py.orig -> overwrite
#
# Run this after: pip install -U voxcpm

$ErrorActionPreference = 'Stop'

# venv is at .venv under the repo root (parent of patches dir)
$repoRoot   = Split-Path -Parent $PSScriptRoot
$venvRoot   = Join-Path $repoRoot '.venv'
$target     = Join-Path $venvRoot 'Lib\site-packages\voxcpm\model\utils.py'
$patchSrc   = Join-Path $PSScriptRoot 'utils.py'
$origBackup = Join-Path $PSScriptRoot 'utils.py.orig'

if (-not (Test-Path -LiteralPath $patchSrc)) {
    Write-Error "Patch source not found: $patchSrc"
    exit 1
}
if (-not (Test-Path -LiteralPath $target)) {
    Write-Error "voxcpm package file not found: $target (is voxcpm installed in .venv?)"
    exit 1
}

$content = Get-Content -LiteralPath $target -Raw

# Already patched -> skip
if ($content -match '_has_xpu') {
    Write-Host 'utils.py already patched with XPU support. Nothing to do.' -ForegroundColor Green
    exit 0
}

# Not patched -> backup original then overwrite
Copy-Item -LiteralPath $target -Destination $origBackup -Force
Write-Host "Backed up original -> $origBackup"

Copy-Item -LiteralPath $patchSrc -Destination $target -Force
Write-Host "Applied XPU patch -> $target" -ForegroundColor Green
Write-Host 'Done. voxcpm now supports device=xpu.' -ForegroundColor Cyan
