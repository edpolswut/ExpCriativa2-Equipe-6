document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("formulario");

    const botoesSenha = document.querySelectorAll(".toggle-senha");

    botoesSenha.forEach(function(botao) {
        botao.addEventListener("click", function () {
            const targetId = botao.getAttribute("data-target");
            const input = document.getElementById(targetId);

            const icon = botao.querySelector("img");

            if (input.type === "password") {
                input.type = "text";
                icon.src = "/icons/eye-off.svg";
            } else {
                input.type = "password";
                icon.src = "/icons/eye.svg";
            }
        });
    });

    form.addEventListener("submit", function (event) {
        event.preventDefault();

        let nome = document.getElementById("nome").value.trim();
        let cpf = document.getElementById("cpf").value.trim().replace(/\D/g, "");
        let email = document.getElementById("email").value.trim();
        let senha = document.getElementById("senha").value.trim();
        let confirmarSenha = document.getElementById("confirmarSenha").value.trim();
        let dataNascimento = document.getElementById("dataNascimento").value;

        let valido = true;

        document.getElementById("erro-nome").textContent = "";
        document.getElementById("erro-cpf").textContent = "";
        document.getElementById("erro-email").textContent = "";
        document.getElementById("erro-senha").textContent = "";
        document.getElementById("erro-confirmar-senha").textContent = "";
        document.getElementById("erro-data").textContent = "";

        if (nome === "") {
            document.getElementById("erro-nome").textContent = "Nome é obrigatório.";
            valido = false;
        } else if (nome.length < 5) {
            document.getElementById("erro-nome").textContent = "Nome deve ter pelo menos 5 caracteres.";
            valido = false;
        }

        if (cpf === "") {
            document.getElementById("erro-cpf").textContent = "CPF é obrigatório.";
            valido = false;
        } else if (cpf.length !== 11) {
            document.getElementById("erro-cpf").textContent = "CPF deve ter 11 dígitos.";
            valido = false;
        }

        let regexEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (email === "") {
            document.getElementById("erro-email").textContent = "Email é obrigatório.";
            valido = false;
        } else if (!regexEmail.test(email)) {
            document.getElementById("erro-email").textContent = "Email inválido.";
            valido = false;
        }

        if (senha === "") {
            document.getElementById("erro-senha").textContent = "Senha é obrigatória.";
            valido = false;
        } else if (senha.length < 8) {
            document.getElementById("erro-senha").textContent = "Senha deve ter pelo menos 8 caracteres.";
            valido = false;
        }

        if (confirmarSenha === "") {
            document.getElementById("erro-confirmar-senha").textContent = "Confirme sua senha.";
            valido = false;
        } else if (senha !== confirmarSenha) {
            document.getElementById("erro-confirmar-senha").textContent = "As senhas não coincidem.";
            valido = false;
        }

        if (dataNascimento === "") {
            document.getElementById("erro-data").textContent = "Data de nascimento é obrigatória.";
            valido = false;
        } else {
            let hoje = new Date();
            let nascimento = new Date(dataNascimento);

            let idade = hoje.getFullYear() - nascimento.getFullYear();
            let mes = hoje.getMonth() - nascimento.getMonth();

            if (mes < 0 || (mes === 0 && hoje.getDate() < nascimento.getDate())) {
                idade--;
            }

            if (idade < 18) {
                document.getElementById("erro-data").textContent = "Você deve ter pelo menos 18 anos.";
                valido = false;
            }
        }

        if (valido) {
            Swal.fire({
                title: "Cadastro realizado com sucesso!",
                text: "Seus dados foram enviados.",
                icon: "success",
                confirmButtonText: "OK"
            }).then(() => {
                form.submit();
            });
        }
    });
});