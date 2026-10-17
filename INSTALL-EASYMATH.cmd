@echo off
chcp 65001 >nul
title 이지매쓰 학원관리 설치
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0deploy\windows\Install-EasyMath.ps1"
echo.
echo 설치 창을 닫으려면 아무 키나 누르세요.
pause >nul
