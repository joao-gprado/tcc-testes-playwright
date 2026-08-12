from playwright.sync_api import expect


def test_excluir_usuario_remove_apenas_a_linha_correta(abrir, capturar):
    page = abrir("dashboard.html")

    linhas = page.locator("#tabela-usuarios tbody tr")
    expect(linhas).to_have_count(3)

    linha_joao = page.locator('#tabela-usuarios tbody tr[data-id="102"]')
    linha_joao.locator(".btn-delete").click()

    expect(linha_joao).to_have_count(0)
    expect(linhas).to_have_count(2)

    capturar("dashboard_usuario_102_removido")
