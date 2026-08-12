from playwright.sync_api import expect


def test_salvar_apelido_fecha_a_modal_e_atualiza_o_perfil(abrir, capturar):
    page = abrir("modal.html")

    modal = page.locator("#modal-perfil")
    page.click("#open-modal-btn")
    expect(modal).to_be_visible()

    page.fill("#novo-apelido", "jp.tester")
    modal.locator("#modal-save").click()

    expect(modal).to_be_hidden()
    expect(page.locator("#perfil-apelido")).to_have_text("jp.tester")

    capturar("modal_apelido_atualizado")
