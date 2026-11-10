@echo off
chcp 65001 > nul
title Criar Novo Tribunal (TRT) - CADERNO DO TRT

echo ========================================================
echo   🏛️ ASSISTENTE DE CRIAÇÃO DE NOVO TRT
echo ========================================================
echo.

python "%~dp0gerar_novo_trt.py"

echo.
pause

