@echo off
setlocal
chcp 65001 >nul
title EasyMath Remote Access Removal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Remove-EasyMathRemote.ps1"
echo.
echo Press any key to close this window.
pause >nul
