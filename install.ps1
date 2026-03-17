# install.ps1 - Install Cursor skills on Windows
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$skillsSource = Join-Path $scriptDir "skills"
$skillsTarget = Join-Path $env:USERPROFILE ".cursor" "skills"

if (-not (Test-Path $skillsTarget)) {
    New-Item -ItemType Directory -Path $skillsTarget -Force | Out-Null
}

$installed = @()
Get-ChildItem -Path $skillsSource -Directory | ForEach-Object {
    $dest = Join-Path $skillsTarget $_.Name
    if (Test-Path $dest) {
        Remove-Item -Path $dest -Recurse -Force
    }
    Copy-Item -Path $_.FullName -Destination $dest -Recurse
    $installed += $_.Name
}

Write-Host ""
Write-Host "Installed $($installed.Count) skill(s) to $skillsTarget" -ForegroundColor Green
$installed | ForEach-Object { Write-Host "  - $_" -ForegroundColor Cyan }
Write-Host ""
Write-Host "Restart Cursor to activate." -ForegroundColor Yellow