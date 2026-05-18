document.addEventListener("DOMContentLoaded", function () {
    const urlParams = new URLSearchParams(window.location.search);
    const botoesSenha = document.querySelectorAll(".toggle-senha");
    const form = document.getElementById("formulario");

    // Toggle de visualização de senha
    botoesSenha.forEach(function (botao) {
        botao.addEventListener("click", function () {
            const targetId = botao.getAttribute("data-target");
            const input = document.getElementById(targetId);
            const icon = botao.querySelector("i");

            if (input.type === "password") {
                input.type = "text";
                icon.classList.replace("fa-eye", "fa-eye-slash");
            } else {
                input.type = "password";
                icon.classList.replace("fa-eye-slash", "fa-eye");
            }
        });
    });

    // Validação de campos vazios antes de enviar (Client-side)
    if (form) {
        form.addEventListener("submit", function (event) {
            const email = document.getElementById("email").value.trim();
            const senha = document.getElementById("senha").value.trim();
            let valido = true;

            // Limpa mensagens de erro anteriores
            const erroEmail = document.getElementById("erro-email");
            const erroSenha = document.getElementById("erro-senha");
            
            if (erroEmail) erroEmail.textContent = "";
            if (erroSenha) erroSenha.textContent = "";

            if (email === "") {
                if (erroEmail) erroEmail.textContent = "Por favor, insira o seu e-mail.";
                valido = false;
            }
            if (senha === "") {
                if (erroSenha) erroSenha.textContent = "Por favor, insira a sua senha.";
                valido = false;
            }

            if (!valido) {
                event.preventDefault(); // Impede o envio do formulário
            }
        });
    }

    // Erros vindos do Servidor (SSR)
    if (urlParams.has('erro')) {
        const erro = urlParams.get('erro');
        if (erro === 'credenciais') {
            Swal.fire({
                icon: 'error',
                title: 'Falha no Login',
                text: 'E-mail ou senha incorretos.',
                confirmButtonColor: '#FFD166'
            });
        } else if (erro === 'sistema') {
            Swal.fire('Erro', 'Ocorreu um erro interno. Tente novamente mais tarde.', 'error');
        }
        // Limpa parâmetros da URL
        window.history.replaceState({}, document.title, window.location.pathname);
    }
});