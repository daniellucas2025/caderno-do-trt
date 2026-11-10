@echo off
chcp 65001 > nul
title [3] Gerar e Publicar Tudo (2 em 1)

echo ========================================================
echo   [3] GERANDO PLATAFORMA E PUBLICANDO NO SITE...
echo ========================================================
echo.

python "%~dp0gerar_e_publicar.py"

echo.
pause

