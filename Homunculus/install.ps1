<#
.SYNOPSIS
    Homunculus Optional Setup Wrapper for Windows.
.DESCRIPTION
    Optional non-admin workspace initializer for Homunculus on Windows.
    If PowerShell script execution is restricted by corporate IT policy, skip this script
    and point your AI assistant directly to HOMUNCULUS_START_HERE.md (Zero-Install Drop-In Mode).
#>
# === DEVELOPER & AI NAVIGATION MAP ===
#   Owning Module : Core Framework Windows PowerShell Installer (`install.ps1`)
#   Callers       : End-user / CI setup (`powershell -ExecutionPolicy Bypass -File .\install.ps1`)
#   Callees       : `scripts/audit_portability.py`, `scripts/homunculus_paths.py`, `scripts/build_adapters.py`
#   Parameters    : -Workspace, -MemoryMode, -Client, -NoAdapters, -PreferCopy, -UseSymlinks, -InstallGitHooks, -DryRun, -Check
#   Section Index : param() (#L16-L28) | Python Discovery (#L33-L41) | -Check/-DryRun (#L47-L58) | Execution (#L60-L88)
# === END NAVIGATION MAP ===
param(
    [string]$Workspace = (Get-Location).Path,
    [ValidateSet("headless", "obsidian")]
    [string]$MemoryMode = "headless",
    [ValidateSet("", "all", "agents_md", "agents-md", "antigravity", "claude_code", "claude-code", "claude_cowork", "claude-cowork", "cursor")]
    [string]$Client = "all",
    [switch]$NoAdapters,
    [switch]$PreferCopy,
    [switch]$UseSymlinks,
    [switch]$InstallGitHooks,
    [switch]$DryRun,
    [switch]$Check
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

$PythonCmd = $null
if (Get-Command "python" -ErrorAction SilentlyContinue) {
    $PythonCmd = "python"
} elseif (Get-Command "py" -ErrorAction SilentlyContinue) {
    $PythonCmd = "py"
} else {
    Write-Error "[WARN] Python 3.10+ not found on PATH. Use Zero-Install Drop-In Mode via HOMUNCULUS_START_HERE.md."
    exit 2
}

$AuditScript = Join-Path $ScriptDir "scripts\audit_portability.py"
$PathsScript = Join-Path $ScriptDir "scripts\homunculus_paths.py"
$AdaptersScript = Join-Path $ScriptDir "scripts\build_adapters.py"

if ($Check) {
    & $PythonCmd $AuditScript --repo $ScriptDir
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    & $PythonCmd $PathsScript --homunculus-root $ScriptDir --workspace $Workspace --check
    exit $LASTEXITCODE
}

if ($DryRun) {
    Write-Output "[DRY-RUN] Would initialize Homunculus in workspace: $Workspace (memory_mode=$MemoryMode, client=$Client)"
    & $PythonCmd $PathsScript --homunculus-root $ScriptDir --workspace $Workspace --check
    exit $LASTEXITCODE
}

if (-not (Test-Path $Workspace)) {
    New-Item -ItemType Directory -Path $Workspace | Out-Null
}

& $PythonCmd $AuditScript --repo $ScriptDir
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& $PythonCmd $PathsScript `
    --homunculus-root $ScriptDir `
    --workspace $Workspace `
    --init-config `
    --memory-mode $MemoryMode `
    --check
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if (-not $NoAdapters -and ($Client -ne "" -or $InstallGitHooks)) {
    $NormalizedClient = if ($Client -ne "") { $Client.Replace("-", "_") } else { "all" }
    $AdapterArgs = @("--homunculus-root", $ScriptDir, "--workspace", $Workspace, "--client", $NormalizedClient)
    if ($PreferCopy -or (-not $UseSymlinks)) {
        # Default to copy mode on Windows (unless -UseSymlinks is passed) to avoid Developer Mode / symlink privilege prompts
        $AdapterArgs += "--prefer-copy"
    }
    if ($InstallGitHooks) {
        $AdapterArgs += "--install-git-hooks"
    }
    & $PythonCmd $AdaptersScript @AdapterArgs
    exit $LASTEXITCODE
}
exit 0
