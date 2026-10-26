var corpo = document.querySelector('#tabela-usuarios tbody');
var toast = document.getElementById('toast');

corpo.addEventListener('click', function (evento) {
  var botao = evento.target;
  if (!botao.classList.contains('btn-delete')) {
    return;
  }

  var linha = botao.closest('tr');
  var id = linha.dataset.id;

  linha.remove();

  toast.textContent = 'Usuário ' + id + ' removido';
  toast.classList.remove('oculto');
});
