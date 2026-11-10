@echo off
chcp 65001 > nul
title [2] Publicar Site no GitHub Pages

echo ========================================================
echo   [2] PUBLICANDO SITE NO GITHUB PAGES...
echo ========================================================
echo.

python "%~dp0publicar_github.py"

echo.
pause

