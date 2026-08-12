from playwright.sync_api import expect


def test_finalizar_compra_exibe_mensagem_de_sucesso(abrir, capturar):
    page = abrir("checkout.html")

    page.fill("#nome", "Maria de Souza")
    page.fill("#email", "maria.souza@email.com")
    page.check("#pag-pix")
    page.check("#termos")
    page.click("#btn-submit")

    mensagem = page.locator("#msg-sucesso")
    expect(mensagem).to_be_visible()
    expect(mensagem).to_have_text("Pedido realizado com sucesso!")

    capturar("checkout_pedido_confirmado")
