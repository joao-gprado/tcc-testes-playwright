## Preparar o ambiente

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium
```

## Rodar os testes

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Rodar um teste só: `pytest tests/test_dashboard.py`

Ver o navegador abrindo: `pytest --headed --slowmo 500`