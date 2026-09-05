# Install nethop and ensure `nethop` works from any new terminal (Windows).
# Usage (PowerShell):
#   irm https://raw.githubusercontent.com/um1chc5/nethop/main/install.ps1 | iex
# Or from a clone:
#   .\install.ps1

$ErrorActionPreference = "Stop"

Write-Host "Installing nethop..." -ForegroundColor Cyan
py -m pip install --user --upgrade "git+https://github.com/um1chc5/nethop.git"

$py = py -c "import sysconfig; print(sysconfig.get_path('scripts', 'nt_user'))"
if (-not $py) {
    # Fallback for older/layout variants
    $ver = py -c "import sys; print(f'{sys.version_info.major}{sys.version_info.minor}')"
    $py = Join-Path $env:APPDATA "Python\Python$ver\Scripts"
}

$scripts = $py.Trim()
if (-not (Test-Path (Join-Path $scripts "nethop.exe"))) {
    # Editable/local wheel sometimes lands in the non-user scripts dir
    $alt = py -c "import sysconfig; print(sysconfig.get_path('scripts'))"
    if ($alt -and (Test-Path (Join-Path $alt.Trim() "nethop.exe"))) {
        $scripts = $alt.Trim()
    }
}

Write-Host "Scripts folder: $scripts" -ForegroundColor DarkGray

$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if (-not $userPath) { $userPath = "" }

$parts = $userPath -split ";" | Where-Object { $_ -and $_.Trim() -ne "" }
if ($parts -notcontains $scripts) {
    $newPath = (@($parts) + $scripts) -join ";"
    [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
    Write-Host "Added to User PATH: $scripts" -ForegroundColor Green
} else {
    Write-Host "Already on User PATH." -ForegroundColor DarkGray
}

# Make this session work immediately
if ($env:Path -notlike "*$scripts*") {
    $env:Path = "$scripts;$env:Path"
}

$cmd = Get-Command nethop -ErrorAction SilentlyContinue
if ($cmd) {
    Write-Host ""
    Write-Host "OK — run:  nethop" -ForegroundColor Green
    Write-Host "(If another already-open terminal still fails, close it and open a new one.)" -ForegroundColor DarkGray
} else {
    Write-Host ""
    Write-Host "Installed, but this shell still cannot see nethop." -ForegroundColor Yellow
    Write-Host "Open a NEW PowerShell window, then type:  nethop" -ForegroundColor Yellow
}
