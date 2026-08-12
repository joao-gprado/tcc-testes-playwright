from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
PASTA_APP = RAIZ / "app"
PASTA_CAPTURAS = RAIZ / "resultados" / "capturas"


@pytest.fixture
def abrir(page):
    def navegar(arquivo):
        page.goto((PASTA_APP / arquivo).as_uri())
        return page

    return navegar


@pytest.fixture
def capturar(page):
    PASTA_CAPTURAS.mkdir(parents=True, exist_ok=True)

    def salvar(nome):
        page.screenshot(path=str(PASTA_CAPTURAS / f"{nome}.png"), full_page=True)

    return salvar
