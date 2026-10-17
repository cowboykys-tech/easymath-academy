[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

function Test-Administrator {
    $Identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $Principal = New-Object Security.Principal.WindowsPrincipal($Identity)
    return $Principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Restart-AsAdministrator {
    $Arguments = @(
        "-NoProfile"
        "-ExecutionPolicy", "Bypass"
        "-File", ('"{0}"' -f $PSCommandPath)
    )
    Start-Process -FilePath "powershell.exe" -Verb RunAs -ArgumentList $Arguments | Out-Null
}

function Find-TailscaleExecutable {
    $Candidates = @()
    if ($env:ProgramFiles) {
        $Candidates += Join-Path $env:ProgramFiles "Tailscale\tailscale.exe"
    }
    if (${env:ProgramFiles(x86)}) {
        $Candidates += Join-Path ${env:ProgramFiles(x86)} "Tailscale\tailscale.exe"
    }
    foreach ($Candidate in $Candidates) {
        if ($Candidate -and (Test-Path $Candidate)) { return $Candidate }
    }
    $Command = Get-Command "tailscale.exe" -ErrorAction SilentlyContinue
    if ($Command) { return $Command.Source }
    return $null
}

function Write-ResultFile {
    param(
        [string]$Path,
        [object]$TailscaleStatus,
        [string]$PublicKeyFingerprint
    )

    $TailnetIp = @($TailscaleStatus.Self.TailscaleIPs | Where-Object { $_ -like "100.*" }) | Select-Object -First 1
    $DnsName = [string]$TailscaleStatus.Self.DNSName
    if ($DnsName) { $DnsName = $DnsName.TrimEnd(".") }
    $Lines = @(
        "이지매쓰 원격 설치 준비 결과"
        "================================"
        "준비 시각: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss K')"
        "컴퓨터 이름: $env:COMPUTERNAME"
        "Windows 사용자: $env:USERNAME"
        "Tailscale 이름: $DnsName"
        "Tailscale IP: $TailnetIp"
        "SSH 포트: 22 (Tailscale 내부에서만 허용)"
        "Mac 공개키 지문: $PublicKeyFingerprint"
        ""
        "비밀번호나 인증키가 들어 있지 않은 연결 확인용 정보입니다."
        "노트북을 전원에 연결하고 Tailscale이 Connected인지 확인해 주세요."
    )
    $Lines | Set-Content -Path $Path -Encoding UTF8
}

if (-not (Test-Administrator)) {
    Write-Host "Windows 관리자 권한을 요청합니다. '예'를 눌러 주세요." -ForegroundColor Yellow
    Restart-AsAdministrator
    exit 0
}

$SetupRoot = Join-Path $env:ProgramData "EasyMathRemote"
$LogRoot = Join-Path $SetupRoot "logs"
$StatePath = Join-Path $SetupRoot "state.json"
$ResultPath = Join-Path ([Environment]::GetFolderPath("Desktop")) "이지매쓰-원격준비결과.txt"
$PublicKeyPath = Join-Path $PSScriptRoot "assets\mac-maintenance-key.pub"
$MacAddressPath = Join-Path $PSScriptRoot "assets\mac-tailscale-addresses.txt"
$OfflineInstallerRoot = Join-Path $PSScriptRoot "offline"
$AuthorizedKeysPath = Join-Path $env:ProgramData "ssh\administrators_authorized_keys"
$FirewallRuleName = "EasyMath-Remote-SSH-Tailscale"

New-Item -ItemType Directory -Path $SetupRoot, $LogRoot -Force | Out-Null
$LogPath = Join-Path $LogRoot ("setup-{0}.log" -f (Get-Date -Format "yyyyMMdd-HHmmss"))
Start-Transcript -Path $LogPath -Force | Out-Null

try {
    Write-Host "[1/7] Windows와 준비파일을 확인합니다."
    $OperatingSystem = Get-CimInstance Win32_OperatingSystem
    if ([version]$OperatingSystem.Version -lt [version]"10.0") {
        throw "Windows 10 이상이 필요합니다. 현재 버전: $($OperatingSystem.Caption)"
    }
    if (-not (Test-Path $PublicKeyPath)) {
        throw "Mac 공개키 파일을 찾을 수 없습니다: $PublicKeyPath"
    }
    if (-not (Test-Path $MacAddressPath)) {
        throw "Mac Tailscale 주소 파일을 찾을 수 없습니다: $MacAddressPath"
    }
    $PublicKey = (Get-Content $PublicKeyPath -Raw).Trim()
    if ($PublicKey -notmatch "^ssh-ed25519\s+[A-Za-z0-9+/=]+\s+easymath-owner-laptop-maintenance$") {
        throw "Mac 공개키 파일 형식이 올바르지 않습니다. 파일을 수정하지 말고 준비 패키지를 다시 받으세요."
    }
    $PublicKeyParts = $PublicKey -split "\s+"
    $PublicKeyBlob = [Convert]::FromBase64String($PublicKeyParts[1])
    $Hasher = [Security.Cryptography.SHA256]::Create()
    try {
        $PublicKeyFingerprint = "SHA256:" + [Convert]::ToBase64String($Hasher.ComputeHash($PublicKeyBlob)).TrimEnd("=")
    } finally {
        $Hasher.Dispose()
    }
    $AllowedMacAddresses = @(Get-Content $MacAddressPath | ForEach-Object { $_.Trim() } | Where-Object { $_ })
    if ($AllowedMacAddresses.Count -eq 0) {
        throw "허용할 Mac Tailscale 주소가 없습니다."
    }
    foreach ($Address in $AllowedMacAddresses) {
        try { [void][Net.IPAddress]::Parse($Address) }
        catch { throw "Mac Tailscale 주소 형식이 올바르지 않습니다: $Address" }
    }

    Write-Host "[2/7] Tailscale 연결을 확인합니다."
    $TailscaleExe = Find-TailscaleExecutable
    if (-not $TailscaleExe) {
        Start-Process "https://tailscale.com/download/windows"
        throw "Tailscale이 설치되어 있지 않습니다. 열린 공식 페이지에서 설치하고 로그인한 뒤 이 파일을 다시 실행하세요."
    }
    $StatusText = (& $TailscaleExe status --json 2>$null) -join "`n"
    if ($LASTEXITCODE -ne 0 -or -not $StatusText) {
        throw "Tailscale 상태를 확인할 수 없습니다. 화면 오른쪽 아래 Tailscale 아이콘에서 로그인한 뒤 다시 실행하세요."
    }
    $TailscaleStatus = $StatusText | ConvertFrom-Json
    if ($TailscaleStatus.BackendState -ne "Running" -or -not $TailscaleStatus.Self.Online) {
        throw "Tailscale이 아직 연결되지 않았습니다. 로그인 후 Connected 상태에서 다시 실행하세요."
    }

    Write-Host "[3/7] 기존 원격 설정 상태를 기록합니다."
    if (-not (Test-Path $StatePath)) {
        $ExistingCapability = Get-WindowsCapability -Online -Name "OpenSSH.Server~~~~0.0.1.0" -ErrorAction SilentlyContinue
        $ExistingService = Get-Service -Name "sshd" -ErrorAction SilentlyContinue
        $ExistingDefaultRule = Get-NetFirewallRule -Name "OpenSSH-Server-In-TCP" -ErrorAction SilentlyContinue
        $State = [ordered]@{
            createdAt = (Get-Date).ToString("o")
            openSshWasInstalled = (($ExistingCapability -and $ExistingCapability.State -eq "Installed") -or [bool]$ExistingService)
            sshdStartupType = if ($ExistingService) { [string]$ExistingService.StartType } else { $null }
            defaultFirewallRuleExisted = [bool]$ExistingDefaultRule
            defaultFirewallRuleWasEnabled = if ($ExistingDefaultRule) { [string]$ExistingDefaultRule.Enabled } else { $null }
            publicKeyFingerprint = $PublicKeyFingerprint
        }
        $State | ConvertTo-Json | Set-Content -Path $StatePath -Encoding UTF8
    }

    Write-Host "[4/7] 압축파일에 포함된 OpenSSH Server를 준비합니다."
    $SshService = Get-Service -Name "sshd" -ErrorAction SilentlyContinue
    if (-not $SshService) {
        $Architecture = [string]$env:PROCESSOR_ARCHITECTURE
        switch ($Architecture.ToUpperInvariant()) {
            "AMD64" {
                $OfflineInstallerName = "OpenSSH-Win64-v10.0.0.0.msi"
                $ExpectedInstallerHash = "ddec9c53864280759cf9f74791cefd387100e3946aa849a1c138a4ed1b96b7d9"
            }
            "ARM64" {
                $OfflineInstallerName = "OpenSSH-ARM64-v10.0.0.0.msi"
                $ExpectedInstallerHash = "7a17d0e22d004fb47ca4bfd8fef926fa305de4ebf70a6f3c7a29c39aabef0023"
            }
            default {
                throw "지원하지 않는 Windows CPU 종류입니다: $Architecture"
            }
        }

        $OfflineInstaller = Join-Path $OfflineInstallerRoot $OfflineInstallerName
        if (-not (Test-Path $OfflineInstaller)) {
            throw "압축파일에 포함된 OpenSSH 설치파일을 찾을 수 없습니다: $OfflineInstallerName"
        }
        $ActualInstallerHash = (Get-FileHash -Path $OfflineInstaller -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($ActualInstallerHash -ne $ExpectedInstallerHash) {
            throw "OpenSSH 설치파일 검증에 실패했습니다. 이 파일을 사용하지 말고 패키지를 다시 받으세요."
        }

        $MsiArguments = "/i `"$OfflineInstaller`" ADDLOCAL=Server /qn /norestart"
        $MsiProcess = Start-Process -FilePath "msiexec.exe" -ArgumentList $MsiArguments -Wait -PassThru
        if ($MsiProcess.ExitCode -notin @(0, 3010)) {
            throw "OpenSSH Server 설치에 실패했습니다. Windows 설치 오류 코드: $($MsiProcess.ExitCode)"
        }
        $SshService = Get-Service -Name "sshd" -ErrorAction SilentlyContinue
        if (-not $SshService) {
            throw "OpenSSH 설치는 끝났지만 sshd 서비스를 찾을 수 없습니다."
        }
    }
    Set-Service -Name "sshd" -StartupType Automatic
    Start-Service -Name "sshd"

    Write-Host "[5/7] Mac 전용 공개키를 등록합니다."
    New-Item -ItemType Directory -Path (Split-Path $AuthorizedKeysPath) -Force | Out-Null
    $CurrentKeys = @()
    if (Test-Path $AuthorizedKeysPath) {
        $CurrentKeys = @(Get-Content $AuthorizedKeysPath | Where-Object { $_.Trim() })
    }
    if ($CurrentKeys -notcontains $PublicKey) {
        $CurrentKeys += $PublicKey
        $CurrentKeys | Set-Content -Path $AuthorizedKeysPath -Encoding ASCII
    }
    & icacls.exe $AuthorizedKeysPath /inheritance:r | Out-Null
    & icacls.exe $AuthorizedKeysPath /grant:r '*S-1-5-18:F' '*S-1-5-32-544:F' | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "SSH 공개키 파일의 Windows 권한 설정에 실패했습니다." }

    Write-Host "[6/7] SSH를 준비한 Mac의 Tailscale 주소에서만 허용합니다."
    $DefaultRule = Get-NetFirewallRule -Name "OpenSSH-Server-In-TCP" -ErrorAction SilentlyContinue
    if ($DefaultRule) { $DefaultRule | Set-NetFirewallRule -Enabled False }
    Get-NetFirewallRule -Name $FirewallRuleName -ErrorAction SilentlyContinue | Remove-NetFirewallRule
    New-NetFirewallRule `
        -Name $FirewallRuleName `
        -DisplayName "EasyMath Remote SSH - prepared Mac only" `
        -Description "이지매쓰 원격 유지보수용 SSH. 준비 패키지를 만든 Mac의 Tailscale 주소만 허용." `
        -Enabled True `
        -Profile Any `
        -Direction Inbound `
        -Action Allow `
        -Protocol TCP `
        -LocalPort 22 `
        -RemoteAddress $AllowedMacAddresses | Out-Null

    Write-Host "[7/7] 재부팅 후 원격 연결을 준비합니다."
    & $TailscaleExe set --unattended=true 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Tailscale 무인 실행을 자동으로 켜지 못했습니다. Tailscale 아이콘 > Preferences > Run unattended를 직접 선택해 주세요."
    }
    Restart-Service -Name "sshd"
    Write-ResultFile -Path $ResultPath -TailscaleStatus $TailscaleStatus -PublicKeyFingerprint $PublicKeyFingerprint

    Write-Host ""
    Write-Host "원격 설치 준비가 완료되었습니다." -ForegroundColor Green
    Write-Host "바탕화면의 '이지매쓰-원격준비결과.txt'를 확인해 주세요."
    Write-Host "비밀번호나 로그인 인증번호는 누구에게도 보내지 마세요."
    exit 0
} catch {
    Write-Host ""
    Write-Host "원격 설치 준비를 완료하지 못했습니다." -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host "문제를 해결한 뒤 START-REMOTE-SETUP.cmd를 다시 실행하세요."
    exit 1
} finally {
    Stop-Transcript | Out-Null
}
