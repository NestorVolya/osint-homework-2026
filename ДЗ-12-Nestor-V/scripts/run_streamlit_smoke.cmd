@echo off
setlocal
cd /d "%~dp0.."
set STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
".venv\Scripts\python.exe" -m streamlit run "scripts\streamlit_smoke_app.py" --server.headless=true --server.address=127.0.0.1 --server.port=8501 --server.fileWatcherType=none > "streamlit-hello.log" 2>&1
echo streamlit exit code: %ERRORLEVEL% >> "streamlit-hello.log"
