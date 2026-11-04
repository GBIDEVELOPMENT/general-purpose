param(
  [string]$Executable = (Join-Path $PSScriptRoot 'PocketKeyboard.Windows.exe')
)
$ErrorActionPreference = 'Stop'
$exe = (Resolve-Path $Executable).Path
$startup = [Environment]::GetFolderPath('Startup')
$shortcut = Join-Path $startup 'PocketKeyboard.lnk'
$shell = New-Object -ComObject WScript.Shell
$link = $shell.CreateShortcut($shortcut)
$link.TargetPath = $exe
$link.WorkingDirectory = Split-Path $exe
$link.Description = 'PocketKeyboard tray receiver'
$link.Save()
Write-Host "Installed per-user sign-in shortcut: $shortcut"
$admin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if ($admin) {
  Get-NetFirewallRule -DisplayName 'PocketKeyboard local receiver' -ErrorAction SilentlyContinue | Remove-NetFirewallRule
  New-NetFirewallRule -DisplayName 'PocketKeyboard local receiver' -Direction Inbound -Action Allow -Protocol TCP -LocalPort 38476 -Profile Private -RemoteAddress LocalSubnet | Out-Null
  Write-Host 'Created private-profile firewall rule restricted to local subnet.'
} else {
  Write-Warning 'Run this script as Administrator once to add the restricted local-network firewall rule. Startup shortcut is installed.'
}
Write-Host "Launch $exe to show the notification-area icon now."
