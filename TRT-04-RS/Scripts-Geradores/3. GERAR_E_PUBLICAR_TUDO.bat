@echo off
chcp 65001 > nul
title [3] Gerar e Publicar Tudo (2 em 1)

echo ========================================================
echo   [3] GERANDO PLATAFORMA E PUBLICANDO NO SITE...
echo ========================================================
echo.

python "%~dp0gerar_plataforma_metas.py"
if %ERRORLEVEL% EQU 0 (
    echo.
    python "%~dp0publicar_github.py"
)

echo.
pause

