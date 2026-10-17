$InstallRoot = Join-Path $env:LOCALAPPDATA "EasyMathAcademy"
. (Join-Path $InstallRoot "config.ps1")
& (Join-Path $InstallRoot "Start-EasyMath.ps1")
Start-Process "http://127.0.0.1:$($env:ACADEMY_PORT)/"
