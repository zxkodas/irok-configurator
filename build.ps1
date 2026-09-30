# Builds IrokConfigurator.exe with the .NET Framework csc.exe that ships with
# Windows, so no toolchain install is required.
#
# Output is a single self-contained ~40 KB exe targeting .NET Framework 4.x,
# which is present on every Windows 10/11. It embeds irok.ico as a resource so
# the icon works even with no network at install time.

$ErrorActionPreference = 'Stop'

$Root     = $PSScriptRoot
$Src      = Join-Path $Root 'src'
$OutDir   = Join-Path $Root 'dist'
$Out      = Join-Path $OutDir 'IrokConfigurator.exe'
$IconSrc  = Join-Path $Root 'assets\irok.ico'
$Csc      = "$env:WINDIR\Microsoft.NET\Framework64\v4.0.30319\csc.exe"

if (-not (Test-Path $Csc)) { throw "csc.exe not found at $Csc" }
if (-not (Test-Path $OutDir)) { New-Item -ItemType Directory -Path $OutDir -Force | Out-Null }

# assets\irok.ico is committed, so this only matters for a partial checkout or a
# hand-copied tree. Pull it from the live site rather than failing the build.
if (-not (Test-Path $IconSrc)) {
    Write-Warning "assets\irok.ico missing, fetching from hid.irok.cn"
    $ProgressPreference = 'SilentlyContinue'
    try {
        Invoke-WebRequest -Uri 'https://hid.irok.cn/favicon.ico' -OutFile $IconSrc -UseBasicParsing -TimeoutSec 20
    } catch {
        throw "icon missing and could not be downloaded: $($_.Exception.Message)"
    }
}
if (-not (Test-Path $IconSrc)) { throw "icon not found at $IconSrc" }

# /win32icon sets the exe icon; /resource embeds the same file so the installer
# can write it to disk for the shortcut to point at.
& $Csc /nologo /target:winexe /optimize+ /platform:anycpu `
    /reference:System.dll `
    /reference:System.Windows.Forms.dll `
    /reference:System.Management.dll `
    "/win32icon:$IconSrc" `
    "/resource:$IconSrc,irok.ico" `
    "/out:$Out" `
    (Join-Path $Src 'IrokConfigurator.cs')

if ($LASTEXITCODE -ne 0) { throw "csc failed with exit code $LASTEXITCODE" }

$fi = Get-Item $Out
Write-Host ""
Write-Host "built  : $($fi.FullName)"
Write-Host ("size   : {0:N0} bytes" -f $fi.Length)
Write-Host ("sha256 : " + (Get-FileHash $Out -Algorithm SHA256).Hash)
