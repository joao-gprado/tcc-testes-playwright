from playwright.sync_api import expect


def test_finalizar_compra_exibe_mensagem_de_sucesso(abrir, curador, capturar):
    page = abrir("checkout.html")

    curador.preencher("#nome", "Maria de Souza", "campo Nome completo do formulário de checkout")
    curador.preencher("#email", "maria.souza@email.com", "campo E-mail do formulário de checkout")
    curador.marcar("#pag-pix", "opção de pagamento PIX")
    curador.marcar("#termos", "caixa de aceite dos Termos e Condições")
    curador.clicar("#btn-submit", "botão Finalizar Compra que envia o pedido")

    mensagem = page.locator("#msg-sucesso")
    expect(mensagem).to_be_visible()
    expect(mensagem).to_have_text("Pedido realizado com sucesso!")

    capturar("checkout_pedido_confirmado")
