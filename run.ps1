$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root
python -m streamlit run "$root\driveshare\app.py"
