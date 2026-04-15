document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("formulario");

    form.addEventListener("submit", function (event) {
        event.preventDefault();

        let nome = document.getElementById("nome").value.trim();
        let email = document.getElementById("email").value.trim();
        let senha = document.getElementById("senha").value.trim();
        let confirmarSenha = document.getElementById("confirmarSenha").value.trim();
        let dataNascimento = document.getElementById("dataNascimento").value;

        let valido = true;

        // Limpar erros
        document.getElementById("erro-nome").textContent = "";
        document.getElementById("erro-email").textContent = "";
        document.getElementById("erro-senha").textContent = "";
        document.getElementById("erro-confirmar-senha").textContent = "";
        document.getElementById("erro-data").textContent = "";



        // Nome
        if (nome === "") {
            document.getElementById("erro-nome").textContent = "Nome é obrigatório.";
            valido = false;
        } else if (nome.length < 5) {
            document.getElementById("erro-nome").textContent = "Nome deve ter pelo menos 5 caracteres.";
            valido = false;
        }

        // Email
        let regexEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (email === "") {
            document.getElementById("erro-email").textContent = "Email é obrigatório.";
            valido = false;
        } else if (!regexEmail.test(email)) {
            document.getElementById("erro-email").textContent = "Email inválido.";
            valido = false;
        }

        // Senha
        if (senha === "") {
            document.getElementById("erro-senha").textContent = "Senha é obrigatória.";
            valido = false;
        } else if (senha.length < 8) {
            document.getElementById("erro-senha").textContent = "Senha deve ter pelo menos 8 caracteres.";
            valido = false;
        }

        // Confirmar senha
        if (confirmarSenha === "") {
            document.getElementById("erro-confirmar-senha").textContent = "Confirme sua senha.";
            valido = false;
        } else if (senha !== confirmarSenha) {
            document.getElementById("erro-confirmar-senha").textContent = "As senhas não coincidem.";
            valido = false;
        }

        // Data de nascimento
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
    alert("Cadastro realizado com sucesso!");
    form.submit();
        }
    });


});