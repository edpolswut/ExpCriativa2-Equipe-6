document.addEventListener("DOMContentLoaded", function () {

    const inputCep = document.getElementById("cep");
    const inputTelefone = document.getElementById("telefone");
    
    inputCep.addEventListener("blur", function() {
        // Remove tudo o que não for número
        let cepVal = this.value.replace(/\D/g, "");

        if (cepVal.length === 8) {
            // Mostra um feedback visual simples enquanto procura
            document.getElementById("logradouro").value = "A procurar...";
            document.getElementById("bairro").value = "A procurar...";
            document.getElementById("cidade").value = "A procurar...";

            fetch(`https://viacep.com.br/ws/${cepVal}/json/`)
                .then(resposta => resposta.json())
                .then(dados => {
                    if (!dados.erro) {
                        // Preenche os campos automaticamente
                        document.getElementById("logradouro").value = dados.logradouro;
                        document.getElementById("bairro").value = dados.bairro;
                        document.getElementById("cidade").value = dados.localidade; // ViaCEP chama a cidade de 'localidade'
                        
                        // Move o foco para o campo "Número" para facilitar a vida do utilizador
                        document.getElementById("numero").focus();
                    } else {
                        // Se o CEP não existir
                        limparCamposEndereco();
                        Swal.fire({
                            icon: 'warning',
                            title: 'CEP não encontrado',
                            text: 'Verifique se digitou corretamente.',
                            confirmButtonColor: '#FFD166'
                        });
                    }
                })
                .catch(erro => {
                    console.error("Erro na API ViaCEP:", erro);
                    limparCamposEndereco();
                });
        }
    });
    
    function limparCamposEndereco() {
        document.getElementById("logradouro").value = "";
        document.getElementById("bairro").value = "";
        document.getElementById("cidade").value = "";
    }

    inputTelefone.addEventListener("input", function () {
        let valor = this.value.replace(/\D/g, "");
        if (valor.length > 11) valor = valor.slice(0, 11);

        if (valor.length > 10) {
            valor = valor.replace(/^(\d{2})(\d{5})(\d{4}).*/, "($1) $2-$3");
        } else if (valor.length > 6) {
            valor = valor.replace(/^(\d{2})(\d{4})(\d{0,4}).*/, "($1) $2-$3");
        } else if (valor.length > 2) {
            valor = valor.replace(/^(\d{2})(\d{0,5}).*/, "($1) $2");
        }
        this.value = valor;
    });

    inputCep.addEventListener("input", function () {
        let valor = this.value.replace(/\D/g, "");
        if (valor.length > 8) valor = valor.slice(0, 8);
        if (valor.length > 5) {
            valor = valor.replace(/^(\d{5})(\d{3}).*/, "$1-$2");
        }
        this.value = valor;
    });

    const form = document.getElementById("formulario");

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

    form.addEventListener("submit", async function (event) {
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

        if (valido) {
            const formData = new FormData(form);
            try {
                const response = await fetch("/CriarLoja", {
                    method: "POST",
                    body: formData
                });

                const resultado = await response.json();

                if (response.ok) {
                    Swal.fire({
                        icon: 'success',
                        title: 'Loja Criada!',
                        text: 'Sua loja foi cadastrada com sucesso.',
                        confirmButtonColor: '#FFD166'
                    }).then(() => {
                        window.location.href = "/perfilLojista";
                    });
                } else {
                    let msg = resultado.erro === 'sistema' ? 'Erro interno no servidor.' : 'Falha ao cadastrar loja.';
                    Swal.fire({ icon: 'error', title: 'Erro', text: msg });
                }
            } catch (error) {
                Swal.fire({ icon: 'error', title: 'Erro', text: 'Falha na conexão com o servidor.' });
            }
        }
    });
});