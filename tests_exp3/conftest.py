from pathlib import Path

import pytest

from self_healing import MiddlewareSelfHealing

RAIZ = Path(__file__).resolve().parent.parent
PASTA_RESULTADOS = RAIZ / "resultados" / "experimento3"


@pytest.fixture
def pasta_app(request):
    return RAIZ / request.config.getoption("--app-dir")


@pytest.fixture
def conjunto(request):
    app_dir = Path(request.config.getoption("--app-dir"))
    return "controle" if app_dir == Path("app") else app_dir.name


@pytest.fixture
def abrir(page, pasta_app):
    def navegar(arquivo):
        page.goto((pasta_app / arquivo).as_uri())
        return page

    return navegar


@pytest.fixture
def curador(request, page, conjunto):
    contexto = {
        "conjunto": conjunto,
        "rodada": request.config.getoption("--rodada"),
        "teste": request.node.name.replace("[chromium]", ""),
    }
    return MiddlewareSelfHealing(
        page,
        PASTA_RESULTADOS / "eventos.jsonl",
        contexto,
        limiar=request.config.getoption("--limiar"),
        modelo=request.config.getoption("--modelo-llm"),
    )


@pytest.fixture
def capturar(page, conjunto):
    pasta = PASTA_RESULTADOS / conjunto / "capturas"
    pasta.mkdir(parents=True, exist_ok=True)

    def salvar(nome):
        page.screenshot(path=str(pasta / f"{nome}.png"), full_page=True)

    return salvar


@pytest.fixture(autouse=True)
def capturar_falha(request, page, conjunto):
    yield
    resultado = getattr(request.node, "resultado_call", None)
    if resultado is not None and resultado.failed:
        pasta = PASTA_RESULTADOS / conjunto / "falhas"
        pasta.mkdir(parents=True, exist_ok=True)
        nome = request.node.name.replace("[chromium]", "")
        page.screenshot(path=str(pasta / f"{nome}.png"), full_page=True)
