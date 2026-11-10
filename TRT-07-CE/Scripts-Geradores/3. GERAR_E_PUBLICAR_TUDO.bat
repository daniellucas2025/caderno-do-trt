@echo off
chcp 65001 > nul
title Gerar e Publicar
python "%~dp0gerar_plataforma_metas.py"
if %ERRORLEVEL% EQU 0 python "%~dp0publicar_github.py"
pause
