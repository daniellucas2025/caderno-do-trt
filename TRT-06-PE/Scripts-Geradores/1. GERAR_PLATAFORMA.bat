@echo off
chcp 65001 > nul
title Gerar Plataforma de Metas
python "%~dp0gerar_plataforma_metas.py"
pause
