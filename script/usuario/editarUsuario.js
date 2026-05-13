document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("formulario");

    form.addEventListener("submit", function (event) {
        event.preventDefault();

        let nome = document.querySelector('input[name="Nome"]').value.trim();
        let email = document.querySelector('input[name="Email"]').value.trim();
        let senha = document.querySelector('input[name="Senha"]').value.trim();

        let valido = true;
        let mensagemErro = "";

        // RegEx para validar formato de e-mail
        let regexEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (nome.length < 3) {
            mensagemErro += "O <b>Nome</b> deve ter pelo menos 3 caracteres.<br>";
            valido = false;
        }

        if (!regexEmail.test(email)) {
            mensagemErro += "O <b>E-mail</b> introduzido não tem um formato válido.<br>";
            valido = false;
        }

        // A senha é opcional na edição, mas se for preenchida, tem de ter no mínimo 8 caracteres
        if (senha !== "" && senha.length < 8) {
            mensagemErro += "A nova <b>Palavra-passe</b> deve ter pelo menos 8 caracteres.<br>";
            valido = false;
        }

        if (!valido) {
            Swal.fire({
                icon: 'error',
                title: 'Verifique os dados',
                html: mensagemErro,
                confirmButtonColor: '#FFD166'
            });
            return;
        }

        form.submit();
    });
});

function confirmarExclusao() {
    Swal.fire({
        title: 'Tem a certeza?',
        text: "Esta ação desativará a sua conta permanentemente!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sim, eliminar!',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            window.location.href = "/DeletarUsuario";
        }
    })
}