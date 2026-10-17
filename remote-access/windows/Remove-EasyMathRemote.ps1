[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

function Test-Administrator {
    $Identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $Principal = New-Object Security.Principal.WindowsPrincipal($Identity)
    return $Principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (-not (Test-Administrator)) {
    $Arguments = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", ('"{0}"' -f $PSCommandPath))
    Start-Process -FilePath "powershell.exe" -Verb RunAs -ArgumentList $Arguments | Out-Null
    exit 0
}

$SetupRoot = Join-Path $env:ProgramData "EasyMathRemote"
$StatePath = Join-Path $SetupRoot "state.json"
$PublicKeyPath = Join-Path $PSScriptRoot "assets\mac-maintenance-key.pub"
$AuthorizedKeysPath = Join-Path $env:ProgramData "ssh\administrators_authorized_keys"
$FirewallRuleName = "EasyMath-Remote-SSH-Tailscale"

if (Test-Path $PublicKeyPath) {
    $PublicKey = (Get-Content $PublicKeyPath -Raw).Trim()
    if (Test-Path $AuthorizedKeysPath) {
        $RemainingKeys = @(Get-Content $AuthorizedKeysPath | Where-Object { $_.Trim() -and $_.Trim() -ne $PublicKey })
        if ($RemainingKeys.Count -gt 0) {
            $RemainingKeys | Set-Content -Path $AuthorizedKeysPath -Encoding ASCII
        } else {
            Remove-Item $AuthorizedKeysPath -Force
        }
    }
}

Get-NetFirewallRule -Name $FirewallRuleName -ErrorAction SilentlyContinue | Remove-NetFirewallRule

if (Test-Path $StatePath) {
    $State = Get-Content $StatePath -Raw | ConvertFrom-Json
    $DefaultRule = Get-NetFirewallRule -Name "OpenSSH-Server-In-TCP" -ErrorAction SilentlyContinue
    if ($DefaultRule -and $State.defaultFirewallRuleExisted) {
        $RestoreEnabled = if ($State.defaultFirewallRuleWasEnabled -eq "True") { "True" } else { "False" }
        $DefaultRule | Set-NetFirewallRule -Enabled $RestoreEnabled
    }
    if (-not $State.openSshWasInstalled) {
        Stop-Service -Name "sshd" -ErrorAction SilentlyContinue
        Set-Service -Name "sshd" -StartupType Disabled -ErrorAction SilentlyContinue
    } elseif ($State.sshdStartupType) {
        Set-Service -Name "sshd" -StartupType $State.sshdStartupType -ErrorAction SilentlyContinue
    }
}

Write-Host "이지매쓰 Mac 공개키와 전용 방화벽 규칙을 제거했습니다." -ForegroundColor Green
Write-Host "Tailscale과 Windows OpenSSH 구성요소는 삭제하지 않았습니다."
