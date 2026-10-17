$ErrorActionPreference = "Stop"
$InstallRoot = Join-Path $env:LOCALAPPDATA "EasyMathAcademy"
$SecretPath = Join-Path $InstallRoot "secrets.json"

if (-not (Test-Path $InstallRoot)) {
    throw "이지매쓰가 아직 설치되지 않았습니다. Install-EasyMath.ps1을 먼저 실행하세요."
}

Write-Host "카카오 REST API 키를 입력하세요. 입력 내용은 화면에 표시되지 않습니다."
$RestKey = Read-Host -AsSecureString
Write-Host "Client Secret을 사용하지 않으면 Enter를 누르세요."
$ClientSecret = Read-Host -AsSecureString
Write-Host "메시지 연결기를 사용하지 않거나 아직 미정이면 Enter를 누르세요."
$MessagingConnectorToken = Read-Host -AsSecureString
Write-Host "OpenAI API 방식을 사용하지 않으면 Enter를 누르세요. Codex 방식에는 필요하지 않습니다."
$OpenAiApiKey = Read-Host -AsSecureString

$Secrets = @{
    kakaoRestApiKey = ConvertFrom-SecureString $RestKey
    kakaoClientSecret = ConvertFrom-SecureString $ClientSecret
    messagingConnectorToken = ConvertFrom-SecureString $MessagingConnectorToken
    openAiApiKey = ConvertFrom-SecureString $OpenAiApiKey
}
$Secrets | ConvertTo-Json | Set-Content -Path $SecretPath -Encoding UTF8
Write-Host "입력한 비밀값을 현재 Windows 사용자만 복호화할 수 있게 저장했습니다."
