# Experimento 2 – executa os mesmos 3 testes contra as páginas originais (controle)
# e contra as variantes V1, V2 e V3, salvando logs, capturas (sucesso e falha) e versões do ambiente.
# Uso (na pasta do projeto, com o ambiente virtual já criado):
#   powershell -ExecutionPolicy Bypass -File .\rodar_experimento2.ps1

$ErrorActionPreference = "Continue"
$py = ".\.venv\Scripts\python.exe"
$saida = "resultados\experimento2"
New-Item -ItemType Directory -Force -Path $saida | Out-Null

# 1) Registro do ambiente
$amb = "$saida\ambiente.txt"
"Data/hora: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Out-File -Encoding utf8 $amb
"Computador: $env:COMPUTERNAME" | Out-File -Encoding utf8 -Append $amb
(Get-CimInstance Win32_OperatingSystem).Caption | Out-File -Encoding utf8 -Append $amb
& $py --version 2>&1 | Out-File -Encoding utf8 -Append $amb
& $py -m pip show pytest pytest-playwright playwright 2>&1 | Select-String "^(Name|Version):" | Out-File -Encoding utf8 -Append $amb
& $py -c "from playwright.sync_api import sync_playwright; p=sync_playwright().start(); b=p.chromium.launch(); print('Chromium', b.version); b.close(); p.stop()" 2>&1 | Out-File -Encoding utf8 -Append $amb
Get-Content $amb

# 2) Execuções: controle + 3 conjuntos de variantes
$conjuntos = @(
  @{ nome = "controle"; pasta = "app" },
  @{ nome = "v1";       pasta = "app_variantes\v1" },
  @{ nome = "v2";       pasta = "app_variantes\v2" },
  @{ nome = "v3";       pasta = "app_variantes\v3" }
)

foreach ($c in $conjuntos) {
  $nome = $c.nome
  Write-Host ""
  Write-Host "==================== $nome ($($c.pasta)) ===================="
  $log = "$saida\log_$nome.txt"
  & $py -m pytest --app-dir $c.pasta -rA 2>&1 |
    ForEach-Object { "$_" } | Tee-Object -Variable linhas
  $linhas | Out-File -Encoding utf8 $log
}

Write-Host ""
Write-Host "Concluído. Logs, capturas e ambiente em: $saida"
