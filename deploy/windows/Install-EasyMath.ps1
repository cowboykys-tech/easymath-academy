$ErrorActionPreference = "Stop"
$SourceRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$InstallRoot = Join-Path $env:LOCALAPPDATA "EasyMathAcademy"

$PythonCandidates = New-Object System.Collections.Generic.List[string]
$PythonRoot = Join-Path $env:LOCALAPPDATA "Programs\Python"
if (Test-Path $PythonRoot) {
    Get-ChildItem $PythonRoot -Filter python.exe -File -Recurse -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -notmatch "\\Scripts\\" } |
        Sort-Object FullName -Descending |
        ForEach-Object { $PythonCandidates.Add($_.FullName) }
}
$PythonCommand = Get-Command python.exe -ErrorAction SilentlyContinue
if ($PythonCommand -and $PythonCommand.Source) {
    $PythonCandidates.Add($PythonCommand.Source)
}
$PyLauncher = Get-Command py.exe -ErrorAction SilentlyContinue
if ($PyLauncher) {
    try {
        $LauncherPython = (& $PyLauncher.Source -3 -c "import sys; print(sys.executable)" 2>$null).Trim()
        if ($LauncherPython) { $PythonCandidates.Add($LauncherPython) }
    } catch { }
}

$PythonPath = $null
$Version = $null
foreach ($Candidate in @($PythonCandidates | Select-Object -Unique)) {
    try {
        $CandidateVersion = (& $Candidate -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null).Trim()
        if ($LASTEXITCODE -eq 0 -and $CandidateVersion -match "^\d+\.\d+$") {
            $PythonPath = $Candidate
            $Version = $CandidateVersion
            break
        }
    } catch { }
}

if (-not $PythonPath) {
    throw "실제로 실행되는 Python 3.11 이상을 찾을 수 없습니다. Python을 설치한 뒤 이 파일을 다시 실행하세요."
}
if ([version]$Version -lt [version]"3.11") { throw "Python 3.11 이상이 필요합니다. 현재 버전: $Version" }

$RequirementsPath = Join-Path $SourceRoot "requirements.txt"
if (-not (Test-Path $RequirementsPath)) {
    throw "Python 필수 패키지 목록을 찾을 수 없습니다. 설치파일을 다시 받으세요."
}
& $PythonPath -m pip install --disable-pip-version-check --quiet --requirement $RequirementsPath
if ($LASTEXITCODE -ne 0) {
    throw "Python 필수 패키지를 설치하지 못했습니다. 인터넷 연결을 확인한 뒤 다시 실행하세요."
}

New-Item -ItemType Directory -Force -Path $InstallRoot, (Join-Path $InstallRoot "data"), (Join-Path $InstallRoot "data\photos"), (Join-Path $InstallRoot "run") | Out-Null
Copy-Item (Join-Path $SourceRoot "server.py"), (Join-Path $SourceRoot "backup.py"), (Join-Path $SourceRoot "README.md"), (Join-Path $SourceRoot "PROJECT_CONTEXT.md"), (Join-Path $SourceRoot "HANDOFF_AND_MAINTENANCE.md") -Destination $InstallRoot -Force
Copy-Item (Join-Path $SourceRoot "dist"), (Join-Path $SourceRoot "connectors") -Destination $InstallRoot -Recurse -Force
Copy-Item (Join-Path $PSScriptRoot "Start-EasyMath.ps1"), (Join-Path $PSScriptRoot "Stop-EasyMath.ps1"), (Join-Path $PSScriptRoot "Backup-EasyMath.ps1"), (Join-Path $PSScriptRoot "Open-EasyMath.ps1"), (Join-Path $PSScriptRoot "Set-EasyMathSecrets.ps1") -Destination $InstallRoot -Force
Copy-Item (Join-Path $PSScriptRoot "config.example.ps1") (Join-Path $InstallRoot "config.ps1") -Force
$PythonPath | Set-Content (Join-Path $InstallRoot "python-path.txt") -Encoding UTF8

Write-Host "원장님 로그인 비밀번호를 설정합니다."
Push-Location $InstallRoot
try { & $PythonPath (Join-Path $InstallRoot "server.py") set-owner-password }
finally { Pop-Location }

$StartAction = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$(Join-Path $InstallRoot 'Start-EasyMath.ps1')`""
$StartTrigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$TaskSettings = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Days 0)
Register-ScheduledTask -TaskName "EasyMath Academy Server" -Action $StartAction -Trigger $StartTrigger -Settings $TaskSettings -Description "이지매쓰 학원관리 서버 자동 시작" -Force | Out-Null

$BackupAction = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$(Join-Path $InstallRoot 'Backup-EasyMath.ps1')`""
$BackupTrigger = New-ScheduledTaskTrigger -Daily -At "22:30"
Register-ScheduledTask -TaskName "EasyMath Academy Backup" -Action $BackupAction -Trigger $BackupTrigger -Settings $TaskSettings -Description "이지매쓰 운영 데이터 자동 백업" -Force | Out-Null

$Shell = New-Object -ComObject WScript.Shell
$Shortcut = $Shell.CreateShortcut((Join-Path ([Environment]::GetFolderPath("Desktop")) "이지매쓰 학원관리.lnk"))
$Shortcut.TargetPath = "powershell.exe"
$Shortcut.Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$(Join-Path $InstallRoot 'Open-EasyMath.ps1')`""
$Shortcut.WorkingDirectory = $InstallRoot
$Shortcut.Save()

& (Join-Path $InstallRoot "Start-EasyMath.ps1")
Write-Host "설치가 완료되었습니다. 바탕화면의 '이지매쓰 학원관리'를 실행하세요."
