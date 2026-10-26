from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent


@pytest.fixture
def pasta_app(request):
    return RAIZ / request.config.getoption("--app-dir")


@pytest.fixture
def pasta_capturas(request):
    app_dir = Path(request.config.getoption("--app-dir"))
    if app_dir == Path("app"):
        return RAIZ / "resultados" / "capturas"
    return RAIZ / "resultados" / "experimento2" / app_dir.name / "capturas"


@pytest.fixture
def abrir(page, pasta_app):
    def navegar(arquivo):
        page.goto((pasta_app / arquivo).as_uri())
        return page

    return navegar


@pytest.fixture
def capturar(page, pasta_capturas):
    pasta_capturas.mkdir(parents=True, exist_ok=True)

    def salvar(nome):
        page.screenshot(path=str(pasta_capturas / f"{nome}.png"), full_page=True)

    return salvar


@pytest.fixture(autouse=True)
def capturar_falha(request, page, pasta_capturas):
    # Se o teste falhar, salva a tela no momento da falha (evidência do Experimento 2)
    yield
    resultado = getattr(request.node, "resultado_call", None)
    if resultado is not None and resultado.failed:
        pasta = pasta_capturas.parent / "falhas"
        pasta.mkdir(parents=True, exist_ok=True)
        nome = request.node.name.replace("[chromium]", "")
        page.screenshot(path=str(pasta / f"{nome}.png"), full_page=True)
