@echo off
cd /d "%~dp0"
where uv >nul 2>nul
if errorlevel 1 (
    echo O uv nao foi encontrado. Instale o uv e abra novamente este arquivo.
    pause
    exit /b 1
)
uv run streamlit run app.py --server.address 127.0.0.1
if errorlevel 1 pause
