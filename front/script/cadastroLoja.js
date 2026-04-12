document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("formulario");

    form.addEventListener("submit", function (event) {
        event.preventDefault();

        let nome = document.getElementById("nome").value.trim();
        let email = document.getElementById("email").value.trim();
        let senha = document.getElementById("senha").value.trim();
        let confirmarSenha = document.getElementById("confirmarSenha").value.trim();
        let dataNascimento = document.getElementById("dataNascimento").value;
        let cnpj = document.getElementById("cnpj").value.trim();
        let logradouro = document.getElementById("logradouro").value.trim();
        let cep = document.getElementById("cep").value.trim();
        let telefone = document.getElementById("telefone").value.trim();

        let valido = true;

        // Limpar erros
        document.getElementById("erro-nome").textContent = "";
        document.getElementById("erro-email").textContent = "";
        document.getElementById("erro-senha").textContent = "";
        document.getElementById("erro-confirmar-senha").textContent = "";
        document.getElementById("erro-data").textContent = "";
        document.getElementById("erro-cnpj").textContent = "";
        document.getElementById("erro-logradouro").textContent = "";
        document.getElementById("erro-cep").textContent = "";
        document.getElementById("erro-telefone").textContent = "";


        //validação CNPJ
        function validarCNPJ(cnpj) {
        cnpj = cnpj.replace(/[^\d]+/g,'');

        if (cnpj.length !== 14) return false;

        if (/^(\d)\1+$/.test(cnpj)) return false;

        let tamanho = cnpj.length - 2;
        let numeros = cnpj.substring(0, tamanho);
        let digitos = cnpj.substring(tamanho);
        let soma = 0;
        let pos = tamanho - 7;

        for (let i = tamanho; i >= 1; i--) {
            soma += numeros.charAt(tamanho - i) * pos--;
            if (pos < 2) pos = 9;
        }

        let resultado = soma % 11 < 2 ? 0 : 11 - soma % 11;
        if (resultado != digitos.charAt(0)) return false;

        tamanho = tamanho + 1;
        numeros = cnpj.substring(0, tamanho);
        soma = 0;
        pos = tamanho - 7;

        for (let i = tamanho; i >= 1; i--) {
            soma += numeros.charAt(tamanho - i) * pos--;
            if (pos < 2) pos = 9;
        }

        resultado = soma % 11 < 2 ? 0 : 11 - soma % 11;
        return resultado == digitos.charAt(1);
        }

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

        // CNPJ
        if (cnpj === "") {
            document.getElementById("erro-cnpj").textContent = "CNPJ é obrigatório.";
            valido = false;
        } else if (!validarCNPJ(cnpj)) {
            document.getElementById("erro-cnpj").textContent = "CNPJ inválido.";
            valido = false;
        }

        // Logradouro
        if (logradouro === "") {
            document.getElementById("erro-logradouro").textContent = "Logradouro é obrigatório.";
            valido = false;
        }

        // CEP (formato 00000-000 ou 00000000)
        let regexCEP = /^\d{5}-?\d{3}$/;
        if (cep === "") {
            document.getElementById("erro-cep").textContent = "CEP é obrigatório.";
            valido = false;
        } else if (!regexCEP.test(cep)) {
            document.getElementById("erro-cep").textContent = "CEP inválido.";
            valido = false;
        }

        // Telefone (formato brasileiro simples)
        let regexTelefone = /^\(?\d{2}\)?\s?\d{4,5}-?\d{4}$/;
        if (telefone === "") {
            document.getElementById("erro-telefone").textContent = "Telefone é obrigatório.";
            valido = false;
        } else if (!regexTelefone.test(telefone)) {
            document.getElementById("erro-telefone").textContent = "Telefone inválido.";
            valido = false;
        }
    
        if (valido) {
    alert("Cadastro realizado com sucesso!");
    form.submit();
        }
    });

    // Botão voltar
    document.getElementById("voltar").addEventListener("click", function () {
        window.location.href = "index.html";
    });

});