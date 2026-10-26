# Experimento 3 – executa os testes com o middleware de self-healing (Gemini) contra as
# páginas originais (controle) e as variantes V1, V2 e V3, registrando cada decisão da IA.
# Uso (na pasta do projeto, com o ambiente virtual criado e GEMINI_API_KEY definida):
#   powershell -ExecutionPolicy Bypass -File .\rodar_experimento3.ps1
#   powershell -ExecutionPolicy Bypass -File .\rodar_experimento3.ps1 -Repeticoes 5 -Limiar 80

param(
  [int]$Repeticoes = 1,
  [int]$Limiar = 80,
  [string]$Modelo = "gemini-3.8-flash"
)

$ErrorActionPreference = "Continue"
$py = ".\.venv\Scripts\python.exe"
$saida = "resultados\experimento3"

if (-not (Test-Path $py)) {
  Write-Host "Ambiente virtual não encontrado. Veja a seção 'Preparar o ambiente' do README."
  exit 1
}
if (-not $env:GEMINI_API_KEY) {
  Write-Host "Defina a variável GEMINI_API_KEY antes de rodar (veja o README)."
  exit 1
}

# Começa uma execução limpa
if (Test-Path $saida) { Remove-Item -Recurse -Force $saida }
New-Item -ItemType Directory -Force -Path $saida | Out-Null

# 1) Registro do ambiente
$amb = "$saida\ambiente.txt"
"Data/hora: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Out-File -Encoding utf8 $amb
"Computador: $env:COMPUTERNAME" | Out-File -Encoding utf8 -Append $amb
(Get-CimInstance Win32_OperatingSystem).Caption | Out-File -Encoding utf8 -Append $amb
& $py --version 2>&1 | Out-File -Encoding utf8 -Append $amb
& $py -m pip show pytest pytest-playwright playwright google-genai 2>&1 | Select-String "^(Name|Version):" | Out-File -Encoding utf8 -Append $amb
& $py -c "from playwright.sync_api import sync_playwright; p=sync_playwright().start(); b=p.chromium.launch(); print('Chromium', b.version); b.close(); p.stop()" 2>&1 | Out-File -Encoding utf8 -Append $amb
"Modelo LLM: $Modelo" | Out-File -Encoding utf8 -Append $amb
"Limiar de confiança: $Limiar%" | Out-File -Encoding utf8 -Append $amb
"Repetições: $Repeticoes" | Out-File -Encoding utf8 -Append $amb
Get-Content $amb

# 2) Execuções: controle + 3 conjuntos de variantes, repetidas
$conjuntos = @(
  @{ nome = "controle"; pasta = "app" },
  @{ nome = "v1";       pasta = "app_variantes\v1" },
  @{ nome = "v2";       pasta = "app_variantes\v2" },
  @{ nome = "v3";       pasta = "app_variantes\v3" }
)

for ($r = 1; $r -le $Repeticoes; $r++) {
  foreach ($c in $conjuntos) {
    $nome = $c.nome
    Write-Host ""
    Write-Host "==================== rodada $r - $nome ($($c.pasta)) ===================="
    $log = "$saida\log_${nome}_r$r.txt"
    & $py -m pytest tests_exp3 --app-dir $c.pasta --limiar $Limiar --modelo-llm $Modelo --rodada $r `
      --junitxml "$saida\junit_${nome}_r$r.xml" -rA 2>&1 |
      ForEach-Object { "$_" } | Tee-Object -Variable linhas
    $linhas | Out-File -Encoding utf8 $log
  }
}

# 3) Resumo das métricas
Write-Host ""
& $py resumir_experimento3.py
Write-Host ""
Write-Host "Concluído. Logs, eventos da IA, capturas e resumo em: $saida"
