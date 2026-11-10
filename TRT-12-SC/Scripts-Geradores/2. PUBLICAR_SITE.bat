@echo off
chcp 65001 > nul
title Publicar no GitHub
python "%~dp0publicar_github.py"
pause
