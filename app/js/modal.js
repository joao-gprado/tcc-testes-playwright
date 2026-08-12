var modal = document.getElementById('modal-perfil');
var campoApelido = document.getElementById('novo-apelido');
var apelidoAtual = document.getElementById('perfil-apelido');

document.getElementById('open-modal-btn').addEventListener('click', function () {
  setTimeout(function () {
    campoApelido.value = apelidoAtual.textContent.trim();
    modal.classList.remove('oculto');
    campoApelido.focus();
  }, 400);
});

document.getElementById('modal-save').addEventListener('click', function () {
  apelidoAtual.textContent = campoApelido.value.trim();
  modal.classList.add('oculto');
});

document.getElementById('modal-cancel').addEventListener('click', function () {
  modal.classList.add('oculto');
});
