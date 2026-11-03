param([switch]$Reset)

# Windows PowerShell 5.1+, Windows 10/11 x64. Never log or pass the API key as a command argument.
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

function Test-LocalPort([int]$Port) {
    $client = New-Object System.Net.Sockets.TcpClient
    try {
        $attempt = $client.BeginConnect("127.0.0.1", $Port, $null, $null)
        if (-not $attempt.AsyncWaitHandle.WaitOne(700)) { return $false }
        try { $client.EndConnect($attempt); return $true } catch { return $false }
    }
    catch { return $false }
    finally { $client.Close() }
}

function Install-OfficialTunnelClient([string]$Target) {
    if (Test-Path -LiteralPath $Target) { return }
    Write-Host "Downloading the verified official OpenAI tunnel-client for Windows x64..."
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    $release = Invoke-RestMethod -Uri "https://api.github.com/repos/openai/tunnel-client/releases/latest" -Headers @{ "User-Agent"="RTorrentBridge-Setup" }
    $assets = @($release.assets | Where-Object { $_.name -match '^tunnel-client-v[0-9][0-9A-Za-z.-]*-windows-amd64\.zip$' })
    if ($assets.Count -ne 1) { throw "Official release does not contain exactly one Windows x64 full tunnel-client ZIP. Download it manually from github.com/openai/tunnel-client/releases." }
    $asset = $assets[0]
    if ($asset.digest -notmatch '^sha256:[0-9a-fA-F]{64}$') { throw "Official release has no SHA-256 digest; refusing unverified binary." }
    if (-not $asset.browser_download_url.StartsWith("https://github.com/openai/tunnel-client/releases/download/")) {
        throw "Unexpected release download URL; refusing."
    }
    $tmp = Join-Path ([IO.Path]::GetTempPath()) ("rtorrent-tunnel-" + [guid]::NewGuid().ToString("N"))
    New-Item -ItemType Directory -Path $tmp -Force | Out-Null
    try {
        $zip = Join-Path $tmp "official.zip"
        Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $zip -UseBasicParsing
        $actual = (Get-FileHash -LiteralPath $zip -Algorithm SHA256).Hash.ToLowerInvariant()
        $expected = $asset.digest.Substring(7).ToLowerInvariant()
        if ($actual -ne $expected) { throw "Official tunnel-client ZIP SHA-256 mismatch. Refusing to install." }
        $unpacked = Join-Path $tmp "unpacked"
        Expand-Archive -LiteralPath $zip -DestinationPath $unpacked -Force
        $matches = @(Get-ChildItem -LiteralPath $unpacked -Recurse -File -Filter "tunnel-client.exe")
        if ($matches.Count -ne 1) { throw "Official ZIP does not contain exactly one tunnel-client.exe." }
        New-Item -ItemType Directory -Path (Split-Path -Parent $Target) -Force | Out-Null
        Copy-Item -LiteralPath $matches[0].FullName -Destination $Target
    }
    finally { Remove-Item -LiteralPath $tmp -Recurse -Force -ErrorAction SilentlyContinue }
    Write-Host "Official tunnel-client installed and SHA-256 verified."
}

function Start-BridgeIfNeeded {
    if (Test-LocalPort 8765) {
        Write-Host "A service is already listening on 127.0.0.1:8765; using it."
        return
    }
    $exe = Join-Path $PSScriptRoot "RTorrentBridge.exe"
    if (-not (Test-Path -LiteralPath $exe)) {
        throw "RTorrentBridge.exe is missing. Extract the full Windows bridge ZIP first."
    }
    Write-Host "Starting rTorrent Bridge locally..."
    Start-Process -FilePath $exe -ArgumentList "serve" -WorkingDirectory $PSScriptRoot
    for ($i = 0; $i -lt 20; $i++) {
        Start-Sleep -Milliseconds 500
        if (Test-LocalPort 8765) { return }
    }
    throw "Bridge did not open port 8765. Check its separate console window."
}

$local = Join-Path $env:LOCALAPPDATA "RTorrentBridge"
$idFile = Join-Path $local "tunnel-id.txt"
$keyFile = Join-Path $local "tunnel-key.dpapi.txt"
$exeFile = Join-Path $local "bin\tunnel-client.exe"

try {
    if ([IntPtr]::Size -ne 8) { throw "Use 64-bit Windows PowerShell on the HP PC." }
    New-Item -ItemType Directory -Path $local -Force | Out-Null
    if ($Reset) {
        Remove-Item -LiteralPath $idFile -Force -ErrorAction SilentlyContinue
        Remove-Item -LiteralPath $keyFile -Force -ErrorAction SilentlyContinue
        Write-Host "Local tunnel pairing cleared. No remote OpenAI resources were deleted."
    }
    Start-BridgeIfNeeded

    if (-not (Test-Path -LiteralPath $idFile)) {
        Write-Host ""
        Write-Host "Create a tunnel at https://platform.openai.com/settings/organization/tunnels"
        Write-Host "Associate it with your ChatGPT workspace, and grant Tunnels Read + Use."
        $tunnelId = (Read-Host "Paste your tunnel_id").Trim()
        if ($tunnelId -cnotmatch '^tunnel_([a-z0-9]{4}_)?[a-z0-9]{32}$') {
            throw "Invalid tunnel_id format. Copy the complete ID from OpenAI Platform."
        }
        Set-Content -LiteralPath $idFile -Value $tunnelId -Encoding ASCII
    }
    else { $tunnelId = (Get-Content -LiteralPath $idFile -Raw).Trim() }
    if ($tunnelId -cnotmatch '^tunnel_([a-z0-9]{4}_)?[a-z0-9]{32}$') {
        throw "Invalid saved tunnel ID. Use Configure-ChatGPT-Tunnel.cmd to re-enter it."
    }

    if (-not (Test-Path -LiteralPath $keyFile)) {
        Write-Host ""
        Write-Host "Create a restricted runtime API key at https://platform.openai.com/settings/organization/api-keys"
        Write-Host "Paste it here, never into ChatGPT, GitHub, or a command argument."
        $secureKey = Read-Host "Paste the runtime API key (input hidden)" -AsSecureString
        if ($secureKey.Length -lt 10) { throw "Runtime API key is missing or incomplete." }
        $dpapiText = ConvertFrom-SecureString -SecureString $secureKey
        Set-Content -LiteralPath $keyFile -Value $dpapiText -Encoding ASCII
        $dpapiText = $null
    }
    else {
        $dpapiText = (Get-Content -LiteralPath $keyFile -Raw).Trim()
        $secureKey = ConvertTo-SecureString -String $dpapiText
        $dpapiText = $null
    }

    Install-OfficialTunnelClient $exeFile

    # The key exists in the child process environment only while the tunnel runs.
    $pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureKey)
    try { $env:CONTROL_PLANE_API_KEY = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer) }
    finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer) }
    $env:CONTROL_PLANE_TUNNEL_ID = $tunnelId
    $env:MCP_SERVER_URL = "http://127.0.0.1:8765/mcp"
    Write-Host ""
    Write-Host "Checking OpenAI tunnel permissions and local MCP connection..."
    & $exeFile doctor --explain
    if ($LASTEXITCODE -ne 0) { throw "Tunnel doctor failed. Verify the Platform organization, tunnel ID, runtime key, and workspace association." }
    Write-Host ""
    Write-Host "Starting ChatGPT tunnel. Keep this window open."
    Write-Host "Tunnel local diagnostics: http://127.0.0.1:8877/ui"
    Write-Host "In ChatGPT: Plugins > + > Add custom MCP server > Connection: Tunnel."
    Write-Host ("Select tunnel ID: " + $tunnelId)
    & $exeFile run --health.listen-addr 127.0.0.1:8877
    if ($LASTEXITCODE -ne 0) { throw "Tunnel client exited with an error. See its diagnostics above." }
}
catch {
    Write-Host ""
    Write-Host ("Setup stopped: " + $_.Exception.Message) -ForegroundColor Red
    exit 1
}
finally {
    Remove-Item Env:\CONTROL_PLANE_API_KEY -ErrorAction SilentlyContinue
    Remove-Item Env:\CONTROL_PLANE_TUNNEL_ID -ErrorAction SilentlyContinue
    Remove-Item Env:\MCP_SERVER_URL -ErrorAction SilentlyContinue
}
