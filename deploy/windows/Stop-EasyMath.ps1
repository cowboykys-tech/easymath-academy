$InstallRoot = Join-Path $env:LOCALAPPDATA "EasyMathAcademy"
$PidPath = Join-Path $InstallRoot "run\server.pid"
if (Test-Path $PidPath) {
    $ServerPid = [int](Get-Content $PidPath -Raw)
    Stop-Process -Id $ServerPid -ErrorAction SilentlyContinue
    Remove-Item $PidPath -Force -ErrorAction SilentlyContinue
}
