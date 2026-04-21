document.addEventListener("DOMContentLoaded", function () {
    
    // 1. VERIFICA MENSAGENS VINDAS DO BACKEND PELA URL
    const urlParams = new URLSearchParams(window.location.search);
    
    if (urlParams.has('erro')) {
        let erro = urlParams.get('erro');
        if (erro === 'credenciais') {
            Swal.fire({ icon: 'error', title: 'Acesso Negado', text: 'E-mail ou palavra-passe incorretos.', confirmButtonColor: '#FFD166' });
        } else if (erro === 'sistema') {
            Swal.fire({ icon: 'error', title: 'Ops!', text: 'Ocorreu um erro no servidor. Tente novamente.', confirmButtonColor: '#FFD166' });
        }
        window.history.replaceState({}, document.title, window.location.pathname);
    }

    if (urlParams.has('sucesso') && urlParams.get('sucesso') === 'cadastro') {
        Swal.fire({ icon: 'success', title: 'Conta criada!', text: 'Inicie sessão para continuar.', confirmButtonColor: '#FFD166' });
        window.history.replaceState({}, document.title, window.location.pathname);
    }

    // 2. VALIDAÇÃO DO FORMULÁRIO (FRONT-END)
    const form = document.getElementById("formulario");

    form.addEventListener("submit", function (event) {
        event.preventDefault();

        let email = document.getElementById("email").value.trim();
        let senha = document.getElementById("senha").value.trim();

        let valido = true;
        let mensagemErro = "";
        let regexEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/; // RegEx de E-mail

        if (!regexEmail.test(email)) {
            mensagemErro += "Introduza um <b>e-mail</b> válido.<br>";
            valido = false;
        }

        if (senha === "") {
            mensagemErro += "A <b>palavra-passe</b> é obrigatória.<br>";
            valido = false;
        }

        if (!valido) {
            Swal.fire({
                icon: 'warning',
                title: 'Campos Inválidos',
                html: mensagemErro,
                confirmButtonColor: '#FFD166'
            });
            return;
        }

        form.submit();
    });
});