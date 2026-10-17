$ErrorActionPreference = "Stop"
$InstallRoot = Join-Path $env:LOCALAPPDATA "EasyMathAcademy"
. (Join-Path $InstallRoot "config.ps1")
$PythonExe = (Get-Content (Join-Path $InstallRoot "python-path.txt") -Raw).Trim()
& $PythonExe (Join-Path $InstallRoot "backup.py") create
if ($LASTEXITCODE -ne 0) { throw "이지매쓰 백업에 실패했습니다." }
