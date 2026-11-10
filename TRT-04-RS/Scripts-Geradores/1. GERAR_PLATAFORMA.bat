@echo off
chcp 65001 > nul
title [1] Gerar Plataforma de Metas

echo ========================================================
echo   [1] GERANDO PLATAFORMA DE METAS LOCALMENTE...
echo ========================================================
echo.

python "%~dp0gerar_plataforma_metas.py"

echo.
pause

