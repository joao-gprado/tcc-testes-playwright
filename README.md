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
## Experimento 2 (variantes)

As páginas alteradas ficam em `app_variantes/`:

| Variante | Tipo de alteração | checkout | dashboard | modal |
|---|---|---|---|---|
| V1 | Mudança legítima (página continua correta) | `#btn-submit` → `#btn-confirmar-pagamento` | classe `btn-delete` → `btn-remover` | `#open-modal-btn` → `#btn-editar-perfil` |
| V2 | Defeito funcional real (mesmos seletores) | regra dos termos invertida | exclui a linha vizinha, mas o aviso informa a 102 | salvar fecha a modal sem atualizar o apelido |
| V3 | Inconsistência estrutural (dois elementos válidos) | dois botões `#btn-submit` | dois botões "Excluir" na linha 102 | dois botões `#open-modal-btn` |

Os testes são os mesmos do Experimento 1; a opção `--app-dir` escolhe a pasta de páginas.

Executar tudo (controle + V1 + V2 + V3), salvando logs, capturas de tela (testes aprovados em `capturas/` e falhas em `falhas/`) e versões do ambiente:

```powershell
powershell -ExecutionPolicy Bypass -File .\rodar_experimento2.ps1
```

Executar um conjunto só: `pytest --app-dir app_variantes/v1`

## Experimento 3 (self-healing com IA)

Os testes de `tests_exp3/` repetem os cenários do Experimento 1, mas cada ação (clicar, preencher, marcar) passa pelo middleware de `self_healing.py`:

1. O seletor original é usado se encontrar exatamente um elemento.
2. Se encontrar 0 ou 2+ elementos, o middleware envia o HTML da página, a ação e a intenção do passo para o Gemini, que devolve um novo seletor e um score de confiança.
3. Score >= limiar (padrão 80%) e novo seletor único: a ação é executada com ele. Caso contrário o teste é abortado (evita bug masking).

As verificações (`expect`) não passam pelo middleware, então um defeito real (V2) continua reprovando o teste.

Chave gratuita do Gemini: criar em https://aistudio.google.com/apikey e definir a variável (depois reabrir o terminal):

```powershell
setx GEMINI_API_KEY "sua-chave"
```

Executar tudo (controle + V1 + V2 + V3):

```powershell
powershell -ExecutionPolicy Bypass -File .\rodar_experimento3.ps1
powershell -ExecutionPolicy Bypass -File .\rodar_experimento3.ps1 -Repeticoes 5 -Limiar 80 -Modelo gemini-3.8-flash
```

Resultados em `resultados/experimento3/`: `eventos.jsonl` (cada chamada à IA: seletor sugerido, confiança, decisão, latência), `resumo.csv` (taxa de resgate, bloqueios e latência por conjunto), `resumo_por_teste.csv`, logs, capturas e `ambiente.txt`.

Executar um conjunto só: `pytest tests_exp3 --app-dir app_variantes/v1`
