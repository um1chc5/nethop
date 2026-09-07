# Install nethop + nmap (and Python/pip if needed) so `nethop` works from a new terminal.
# Usage (PowerShell):
#   irm https://raw.githubusercontent.com/um1chc5/nethop/main/install.ps1 | iex
# Or from a clone:
#   .\install.ps1
#
# One script: installs nmap via winget/choco/scoop when missing (asks Y/n first).
# Prompts default to Yes. Non-interactive: $env:NETHOP_YES = "1"

$ErrorActionPreference = "Stop"

function Confirm-Yes([string]$Prompt) {
    if ($env:NETHOP_YES -eq "1") {
        Write-Host "$Prompt [Y/n] Y"
        return $true
    }
    try {
        $ans = Read-Host "$Prompt [Y/n]"
    } catch {
        Write-Host "$Prompt — could not prompt; skipping (set NETHOP_YES=1 to auto-accept)."
        return $false
    }
    if ([string]::IsNullOrWhiteSpace($ans)) { return $true }
    return $ans -match '^[Yy]'
}

function Test-Cmd([string]$Name) {
    return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

function Refresh-NmapPath {
    $candidates = @(
        "${env:ProgramFiles(x86)}\Nmap",
        "$env:ProgramFiles\Nmap"
    )
    foreach ($dir in $candidates) {
        $exe = Join-Path $dir "nmap.exe"
        if (Test-Path $exe) {
            if ($env:Path -notlike "*$dir*") {
                $env:Path = "$dir;$env:Path"
            }
            return $true
        }
    }
    return $false
}

function Ensure-Python {
    if (Test-Cmd "py") {
        Write-Host "Python found (py launcher)."
        return
    }
    if (Test-Cmd "python") {
        Write-Host "Python found."
        return
    }
    Write-Host "Python 3.10+ is required."
    if (-not (Confirm-Yes "Install Python now (winget)?")) {
        throw "Install Python 3.10+ from https://www.python.org/downloads/ then re-run."
    }
    if (-not (Test-Cmd "winget")) {
        throw "winget not found. Install Python from https://www.python.org/downloads/ then re-run."
    }
    winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
    Write-Host "If 'py' is still missing, close this window and run the installer again." -ForegroundColor Yellow
}

function Test-Nmap {
    if (Test-Cmd "nmap") { return $true }
    Refresh-NmapPath | Out-Null
    return (Test-Cmd "nmap")
}

function Ensure-Nmap {
    if (Test-Nmap) {
        Write-Host "nmap found."
        return
    }
    Write-Host "nmap is required (system package — this script installs it for you)."
    if (-not (Confirm-Yes "Install nmap now?")) {
        throw "nmap is required. Re-run and answer Y, or install nmap then re-run."
    }
    if (Test-Cmd "winget") {
        winget install -e --id Insecure.Nmap --accept-package-agreements --accept-source-agreements
    } elseif (Test-Cmd "choco") {
        choco install nmap -y
    } elseif (Test-Cmd "scoop") {
        scoop install nmap
    } else {
        Start-Process "https://nmap.org/download.html"
        throw "No winget/choco/scoop. Install nmap from the opened page (include Npcap), then re-run."
    }
    # winget often installs under Program Files but PATH needs a refresh
    $nmapDirs = @(
        "${env:ProgramFiles(x86)}\Nmap",
        "$env:ProgramFiles\Nmap"
    )
    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if (-not $userPath) { $userPath = "" }
    foreach ($dir in $nmapDirs) {
        if ((Test-Path (Join-Path $dir "nmap.exe")) -and ($userPath -notlike "*$dir*")) {
            $userPath = if ($userPath) { "$userPath;$dir" } else { $dir }
            [Environment]::SetEnvironmentVariable("Path", $userPath, "User")
            Write-Host "Added to User PATH: $dir" -ForegroundColor Green
        }
    }
    if (Test-Nmap) {
        Write-Host "nmap installed." -ForegroundColor Green
    } else {
        throw "nmap was installed but is not on PATH yet. Open a NEW PowerShell window and re-run if needed."
    }
}

Write-Host "Installing nethop..." -ForegroundColor Cyan

Ensure-Python
Ensure-Nmap

$prevEap = $ErrorActionPreference
$ErrorActionPreference = "Continue"
py -m pip --version | Out-Null
$pipOk = ($LASTEXITCODE -eq 0)
$ErrorActionPreference = $prevEap
if (-not $pipOk) {
    if (Confirm-Yes "pip is missing. Bootstrap pip (ensurepip)?") {
        py -m ensurepip --user --upgrade
    } else {
        throw "pip is required. Re-run after installing pip."
    }
}

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
