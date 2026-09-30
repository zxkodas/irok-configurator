# Thin wrapper kept so the old entry point still works.
#
# The PowerShell approach this replaced pointed its shortcut straight at
# chrome.exe, which meant the entry was a Chrome shortcut in every sense: Chrome's
# identity in the taskbar and Start menu, and no runtime browser detection.
#
# The real launcher (dist\IrokConfigurator.exe) points its shortcuts at itself and
# resolves the browser at launch time, preferring Edge and falling back to Chrome,
# Brave, Opera and Vivaldi. Use that.
#
# This script just runs it, so re-running this never recreates the old shortcut.

$ErrorActionPreference = 'Stop'

$Root = $PSScriptRoot
$Exe  = Join-Path $Root 'dist\IrokConfigurator.exe'

if (-not (Test-Path $Exe)) {
    throw "Launcher not found: $Exex`nBuild it first:  powershell -ExecutionPolicy Bypass -File `"$Root\build.ps1`""
}

# No --silent: we want the install confirmation and any error dialog.
Start-Process -FilePath $Exe -Wait
