document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("formulario");
    const botoesSenha = document.querySelectorAll(".toggle-senha");

    const inputNome = document.getElementById("nome");
    const inputCpf = document.getElementById("cpf");
    const inputData = document.getElementById("dataNascimento");

    botoesSenha.forEach(function (botao) {
        botao.addEventListener("click", function () {
            const targetId = botao.getAttribute("data-target");
            const input = document.getElementById(targetId);
            const icon = botao.querySelector("img");

            if (input.type === "password") {
                input.type = "text";
                icon.src = "/front/icons/eye-off.svg";
            } else {
                input.type = "password";
                icon.src = "/front/icons/eye.svg";
            }
        });
    });

    // NOME: não deixa digitar números
    inputNome.addEventListener("input", function () {
        this.value = this.value.replace(/[0-9]/g, "");
    });

    // CPF: só permite números e aplica máscara 000.000.000-00
    inputCpf.addEventListener("input", function () {
        let valor = this.value.replace(/\D/g, "");

        if (valor.length > 11) {
            valor = valor.slice(0, 11);
        }

        if (valor.length > 9) {
            valor = valor.replace(/^(\d{3})(\d{3})(\d{3})(\d{1,2}).*/, "$1.$2.$3-$4");
        } else if (valor.length > 6) {
            valor = valor.replace(/^(\d{3})(\d{3})(\d{1,3}).*/, "$1.$2.$3");
        } else if (valor.length > 3) {
            valor = valor.replace(/^(\d{3})(\d{1,3}).*/, "$1.$2");
        }

        this.value = valor;
    });

    // DATA DE NASCIMENTO: não deixa ano com mais de 4 dígitos
    inputData.addEventListener("input", function () {
        let valor = this.value;

        // Caso o input esteja no formato yyyy-mm-dd
        if (valor.includes("-")) {
            let partes = valor.split("-");

            if (partes[0] && partes[0].length > 4) {
                partes[0] = partes[0].slice(0, 4);
                this.value = partes.join("-");
            }
        }
    });

    form.addEventListener("submit", function (event) {
        event.preventDefault();

        let nome = inputNome.value.trim();
        let cpf = inputCpf.value.replace(/\D/g, "");
        let email = document.getElementById("email").value.trim();
        let senha = document.getElementById("senha").value.trim();
        let confirmarSenha = document.getElementById("confirmarSenha").value.trim();
        let dataNascimento = inputData.value;

        let valido = true;

        document.getElementById("erro-nome").textContent = "";
        document.getElementById("erro-cpf").textContent = "";
        document.getElementById("erro-email").textContent = "";
        document.getElementById("erro-senha").textContent = "";
        document.getElementById("erro-confirmar-senha").textContent = "";
        document.getElementById("erro-data").textContent = "";

        const regexNome = /^[A-Za-zÀ-ÿ\s]+$/;
        const regexEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        const regexSenhaForte = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&.#_\-])[A-Za-z\d@$!%*?&.#_\-]{8,}$/;

        if (nome === "") {
            document.getElementById("erro-nome").textContent = "Nome é obrigatório.";
            valido = false;
        } else if (nome.length < 5) {
            document.getElementById("erro-nome").textContent = "Nome deve ter pelo menos 5 caracteres.";
            valido = false;
        } else if (!regexNome.test(nome)) {
            document.getElementById("erro-nome").textContent = "Nome não pode conter números.";
            valido = false;
        }

        if (cpf === "") {
            document.getElementById("erro-cpf").textContent = "CPF é obrigatório.";
            valido = false;
        } else if (cpf.length !== 11) {
            document.getElementById("erro-cpf").textContent = "CPF deve ter 11 dígitos.";
            valido = false;
        }

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
        } else if (!regexSenhaForte.test(senha)) {
            document.getElementById("erro-senha").textContent =
                "A senha deve ter pelo menos 8 caracteres, com maiúscula, minúscula, número e caractere especial.";
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
            let partes = dataNascimento.split("-");

            if (partes[0] && partes[0].length > 4) {
                document.getElementById("erro-data").textContent = "O ano da data deve ter no máximo 4 dígitos.";
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