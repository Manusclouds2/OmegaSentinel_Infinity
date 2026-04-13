$env:PYTHONPATH = ".;./src;./src/monitors;./src/services"
.\.venv\Scripts\activate.ps1
python -I app.py --mode protection --stealth
