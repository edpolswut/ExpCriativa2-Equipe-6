document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("formulario");

    form.addEventListener("submit", function (event) {
        event.preventDefault();

        let nomeLoja = document.getElementById("nomeLoja").value.trim();
        let emailLoja = document.getElementById("emailLoja").value.trim();
        let cnpj = document.getElementById("cnpj").value.trim();
        let logradouro = document.getElementById("logradouro").value.trim();
        let cep = document.getElementById("cep").value.trim();
        let telefone = document.getElementById("telefone").value.trim();

        let valido = true;

        // Limpar erros
        document.getElementById("erro-nomeLoja").textContent = "";
        document.getElementById("erro-emailLoja").textContent = "";
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

        // nomeLoja
        if (nomeLoja === "") {
            document.getElementById("erro-nomeLoja").textContent = "Nome da loja é obrigatório.";
            valido = false;
        } else if (nomeLoja.length > 20) {
            document.getElementById("erro-nomeLoja").textContent = "Nome da loja deve ter menos de 20 caractéres.";
            valido = false;
        }

        // emailLoja
        let regexEmailLoja = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (emailLoja === "") {
            document.getElementById("erro-emailLoja").textContent = "E-mail da loja é obrigatório.";
            valido = false;
        } else if (!regexEmailLoja.test(emailLoja)) {
            document.getElementById("erro-emailLoja").textContent = "E-mail da loja inválido.";
            valido = false;
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