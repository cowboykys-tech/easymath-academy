@echo off
setlocal
chcp 65001 >nul
title EasyMath Remote Setup
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Prepare-EasyMathRemote.ps1"
set "SETUP_EXIT=%ERRORLEVEL%"
echo.
if not "%SETUP_EXIT%"=="0" (
  echo Setup did not finish. Review the message above and run this file again.
) else (
  echo EasyMath remote setup finished.
)
echo.
echo Press any key to close this window.
pause >nul
exit /b %SETUP_EXIT%
