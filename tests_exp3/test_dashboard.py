from playwright.sync_api import expect


def test_excluir_usuario_remove_apenas_a_linha_correta(abrir, curador, capturar):
    page = abrir("dashboard.html")

    linhas = page.locator("#tabela-usuarios tbody tr")
    expect(linhas).to_have_count(3)

    linha_joao = page.locator('#tabela-usuarios tbody tr[data-id="102"]')
    curador.clicar(
        '#tabela-usuarios tbody tr[data-id="102"] .btn-delete',
        "botão Excluir da linha do usuário 102 (João Silva) na tabela de usuários",
    )

    expect(linha_joao).to_have_count(0)
    expect(linhas).to_have_count(2)

    capturar("dashboard_usuario_102_removido")
