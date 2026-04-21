document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("formulario");

    // ====== BUSCA DE CEP (ViaCEP) ======
    const cepInput = document.getElementById("cep");

    cepInput.addEventListener("blur", function () {
        let cep = cepInput.value.replace(/\D/g, "");

        if (cep.length !== 8) return;

        fetch(`https://viacep.com.br/ws/${cep}/json/`)
            .then(response => response.json())
            .then(data => {
                if (data.erro) {
                    Swal.fire({
                        icon: "error",
                        title: "CEP não encontrado",
                        text: "Verifique o CEP digitado."
                    });
                    return;
                }

                document.getElementById("logradouro").value = data.logradouro || "";
                document.getElementById("bairro").value = data.bairro || "";
                document.getElementById("cidade").value = data.localidade || "";
            })
            .catch(() => {
                Swal.fire({
                    icon: "error",
                    title: "Erro ao buscar CEP",
                    text: "Não foi possível consultar o CEP."
                });
            });
    });

    // ====== VALIDAÇÃO DE CNPJ ======
    function validarCNPJ(cnpj) {
        cnpj = cnpj.replace(/[^\d]+/g, "");

        if (cnpj.length !== 14) return false;
        if (/^(\d)\1+$/.test(cnpj)) return false;

        let tamanho = cnpj.length - 2;
        let numeros = cnpj.substring(0, tamanho);
        let digitos = cnpj.substring(tamanho);
        let soma = 0;
        let pos = tamanho - 7;

        for (let i = tamanho; i >= 1; i--) {
            soma += Number(numeros.charAt(tamanho - i)) * pos--;
            if (pos < 2) pos = 9;
        }

        let resultado = soma % 11 < 2 ? 0 : 11 - (soma % 11);
        if (resultado !== Number(digitos.charAt(0))) return false;

        tamanho = tamanho + 1;
        numeros = cnpj.substring(0, tamanho);
        soma = 0;
        pos = tamanho - 7;

        for (let i = tamanho; i >= 1; i--) {
            soma += Number(numeros.charAt(tamanho - i)) * pos--;
            if (pos < 2) pos = 9;
        }

        resultado = soma % 11 < 2 ? 0 : 11 - (soma % 11);
        return resultado === Number(digitos.charAt(1));
    }

    // ====== SUBMIT DO FORMULÁRIO ======
    form.addEventListener("submit", function (event) {
        event.preventDefault();

        let nomeLoja = document.getElementById("nomeLoja").value.trim();
        let emailLoja = document.getElementById("emailLoja").value.trim();
        let cnpj = document.getElementById("cnpj").value.trim().replace(/\D/g, "");
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

        // Nome da loja
        if (nomeLoja === "") {
            document.getElementById("erro-nomeLoja").textContent = "Nome da loja é obrigatório.";
            valido = false;
        } else if (nomeLoja.length > 20) {
            document.getElementById("erro-nomeLoja").textContent = "Nome da loja deve ter menos de 20 caracteres.";
            valido = false;
        }

        // E-mail da loja
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

        // CEP
        let regexCEP = /^\d{5}-?\d{3}$/;
        if (cep === "") {
            document.getElementById("erro-cep").textContent = "CEP é obrigatório.";
            valido = false;
        } else if (!regexCEP.test(cep)) {
            document.getElementById("erro-cep").textContent = "CEP inválido.";
            valido = false;
        }

        // Telefone
        let regexTelefone = /^\(?\d{2}\)?\s?\d{4,5}-?\d{4}$/;
        if (telefone === "") {
            document.getElementById("erro-telefone").textContent = "Telefone é obrigatório.";
            valido = false;
        } else if (!regexTelefone.test(telefone)) {
            document.getElementById("erro-telefone").textContent = "Telefone inválido.";
            valido = false;
        }

        // Envio com SweetAlert
        if (valido) {
            Swal.fire({
                title: "Cadastro realizado com sucesso!",
                text: "Os dados da loja foram enviados.",
                icon: "success",
                confirmButtonText: "OK"
            }).then(() => {
                form.submit();
            });
        }
    });
});
