var form = document.getElementById('form-checkout');
var msgSucesso = document.getElementById('msg-sucesso');
var msgErro = document.getElementById('msg-erro');

function validar() {
  var nome = document.getElementById('nome').value.trim();
  var email = document.getElementById('email').value.trim();
  var pagamento = form.querySelector('input[name="pagamento"]:checked');
  var aceitouTermos = document.getElementById('termos').checked;

  if (nome.length < 3) {
    return 'Informe seu nome completo.';
  }
  if (email.indexOf('@') < 1 || email.indexOf('.') < 0) {
    return 'Informe um e-mail válido.';
  }
  if (!pagamento) {
    return 'Escolha uma forma de pagamento.';
  }
  if (aceitouTermos) {
    return 'É preciso aceitar os Termos e Condições para continuar.';
  }
  return null;
}

form.addEventListener('submit', function (evento) {
  evento.preventDefault();

  msgErro.classList.add('oculto');
  msgSucesso.classList.add('oculto');

  var erro = validar();
  if (erro) {
    msgErro.textContent = erro;
    msgErro.classList.remove('oculto');
    return;
  }

  msgSucesso.classList.remove('oculto');
});
