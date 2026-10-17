$ErrorActionPreference = "Stop"
$InstallRoot = Join-Path $env:LOCALAPPDATA "EasyMathAcademy"
$ConfigPath = Join-Path $InstallRoot "config.ps1"
$SecretPath = Join-Path $InstallRoot "secrets.json"
$PidPath = Join-Path $InstallRoot "run\server.pid"

if (-not (Test-Path $ConfigPath)) { throw "이지매쓰 설정 파일을 찾을 수 없습니다." }
. $ConfigPath

if (Test-Path $SecretPath) {
    $Secrets = Get-Content $SecretPath -Raw | ConvertFrom-Json
    foreach ($Pair in @(
        @("KAKAO_REST_API_KEY", $Secrets.kakaoRestApiKey),
        @("KAKAO_CLIENT_SECRET", $Secrets.kakaoClientSecret),
        @("ACADEMY_MESSAGING_CONNECTOR_TOKEN", $Secrets.messagingConnectorToken),
        @("OPENAI_API_KEY", $Secrets.openAiApiKey)
    )) {
        if ($Pair[1]) {
            $Secure = ConvertTo-SecureString $Pair[1]
            $Pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($Secure)
            try { [Environment]::SetEnvironmentVariable($Pair[0], [Runtime.InteropServices.Marshal]::PtrToStringBSTR($Pointer), "Process") }
            finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($Pointer) }
        }
    }
}

New-Item -ItemType Directory -Force -Path (Split-Path $PidPath) | Out-Null
if (Test-Path $PidPath) {
    $ExistingPid = [int](Get-Content $PidPath -Raw)
    if (Get-Process -Id $ExistingPid -ErrorAction SilentlyContinue) { exit 0 }
}

$PythonExe = (Get-Content (Join-Path $InstallRoot "python-path.txt") -Raw).Trim()
$Process = Start-Process -FilePath $PythonExe -ArgumentList @((Join-Path $InstallRoot "server.py")) -WorkingDirectory $InstallRoot -WindowStyle Hidden -PassThru
$Process.Id | Set-Content -Path $PidPath -Encoding ASCII

for ($Attempt = 0; $Attempt -lt 20; $Attempt++) {
    Start-Sleep -Milliseconds 500
    try {
        Invoke-WebRequest "http://127.0.0.1:$($env:ACADEMY_PORT)/api/config" -UseBasicParsing -TimeoutSec 2 | Out-Null
        exit 0
    } catch { }
}
throw "이지매쓰 서버가 시작되지 않았습니다."
