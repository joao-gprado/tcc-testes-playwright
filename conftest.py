import pytest


def pytest_addoption(parser):
    # Experimento 1: pasta "app" (padrão). Experimento 2: app_variantes/v1, v2 ou v3.
    parser.addoption(
        "--app-dir",
        default="app",
        help="Pasta com as páginas HTML a testar (padrão: app)",
    )
    # Experimento 3: middleware de self-healing
    parser.addoption("--limiar", type=int, default=80, help="Confiança mínima (%%) para aceitar o novo seletor")
    parser.addoption("--modelo-llm", default="gemini-3.8-flash", help="Modelo Gemini usado no self-healing")
    parser.addoption("--rodada", type=int, default=1, help="Número da repetição (registrado nos eventos)")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # Guarda o resultado de cada fase do teste para a captura de falhas
    outcome = yield
    relatorio = outcome.get_result()
    setattr(item, f"resultado_{relatorio.when}", relatorio)
