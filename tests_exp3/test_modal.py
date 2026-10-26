from playwright.sync_api import expect


def test_salvar_apelido_fecha_a_modal_e_atualiza_o_perfil(abrir, curador, capturar):
    page = abrir("modal.html")

    modal = page.locator("#modal-perfil")
    curador.clicar("#open-modal-btn", "botão Editar Perfil que abre a modal de edição do perfil")
    expect(modal).to_be_visible()

    curador.preencher("#novo-apelido", "jp.tester", "campo Novo Apelido dentro da modal de perfil")
    curador.clicar("#modal-perfil #modal-save", "botão Salvar Alterações da modal de perfil")

    expect(modal).to_be_hidden()
    expect(page.locator("#perfil-apelido")).to_have_text("jp.tester")

    capturar("modal_apelido_atualizado")
