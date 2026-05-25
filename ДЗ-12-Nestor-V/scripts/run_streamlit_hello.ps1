$ErrorActionPreference = "Continue"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $Root

$Python = Join-Path $Root ".venv\Scripts\python.exe"
$Log = Join-Path $Root "streamlit-hello.log"

$env:STREAMLIT_BROWSER_GATHER_USAGE_STATS = "false"
& $Python -m streamlit run ".\scripts\streamlit_smoke_app.py" --server.headless=true --server.address=127.0.0.1 --server.port=8501 --server.fileWatcherType=none > $Log 2>&1
