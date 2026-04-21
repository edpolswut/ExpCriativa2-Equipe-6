document.addEventListener("DOMContentLoaded", function () {

    const form = document.querySelector('form[action="/SalvarEdicaoLoja"]');

    const inputCnpj = document.querySelector('input[name="Cnpj"]');
    const inputTel = document.querySelector('input[name="Telefone"]');
    const inputCep = document.querySelector('input[name="Cep"]');
    
    if (inputCep) {
        inputCep.addEventListener("blur", function() {
            let cepVal = this.value.replace(/\D/g, "");

            if (cepVal.length === 8) {
                const inputRua = document.querySelector('input[name="Rua"]');
                const inputBairro = document.querySelector('input[name="Bairro"]');
                const inputCidade = document.querySelector('input[name="Cidade"]');
                const inputNumero = document.querySelector('input[name="Numero"]');

                inputRua.value = "A procurar...";
                inputBairro.value = "A procurar...";
                inputCidade.value = "A procurar...";

                fetch(`https://viacep.com.br/ws/${cepVal}/json/`)
                    .then(resposta => resposta.json())
                    .then(dados => {
                        if (!dados.erro) {
                            inputRua.value = dados.logradouro;
                            inputBairro.value = dados.bairro;
                            inputCidade.value = dados.localidade;
                            inputNumero.focus();
                        } else {
                            inputRua.value = "";
                            inputBairro.value = "";
                            inputCidade.value = "";
                            Swal.fire({
                                icon: 'warning',
                                title: 'CEP não encontrado',
                                confirmButtonColor: '#FFD166'
                            });
                        }
                    })
                    .catch(erro => console.error("Erro ViaCEP:", erro));
            }
        });
    }

    const aplicarMascara = (el, maskFn) => {
        el.addEventListener("input", e => { e.target.value = maskFn(e.target.value); });
    };

    aplicarMascara(inputCnpj, v => v.replace(/\D/g,"").replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, "$1.$2.$3/$4-$5").substring(0, 18));
    aplicarMascara(inputTel, v => v.replace(/\D/g,"").replace(/^(\d{2})(\d{5})(\d{4})/, "($1) $2-$3").substring(0, 15));
    aplicarMascara(inputCep, v => v.replace(/\D/g,"").replace(/^(\d{5})(\d{3})/, "$1-$2").substring(0, 9));

    // --- PREVIEW DE IMAGENS ---
    function setupPreview(inputId, imgId) {
        document.getElementById(inputId).addEventListener("change", function(e) {
            const reader = new FileReader();
            reader.onload = function(event) {
                document.getElementById(imgId).src = event.target.result;
            };
            if (e.target.files[0]) reader.readAsDataURL(e.target.files[0]);
        });
    }

    setupPreview("input-logo", "preview-logo");
    setupPreview("input-banner", "preview-banner");

    // Função de validação de CNPJ (Reaproveitada do seu código)
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
        if (resultado !== Number(digitos.charAt(1))) return false;

        return true;
    }

    form.addEventListener("submit", function (event) {
        // Impede o envio imediato para podermos validar
        event.preventDefault();

        let cnpj = document.querySelector('input[name="Cnpj"]').value.trim();
        let cep = document.querySelector('input[name="Cep"]').value.trim();
        let telefone = document.querySelector('input[name="Telefone"]').value.trim();

        let valido = true;
        let mensagemErro = "";

        // RegEx para CEP (ex: 12345-678 ou 12345678) e Telefone
        let regexCEP = /^\d{5}-?\d{3}$/;
        let regexTelefone = /^\(?\d{2}\)?\s?\d{4,5}-?\d{4}$/;

        if (!validarCNPJ(cnpj)) {
            mensagemErro += "O <b>CNPJ</b> informado é inválido.<br>";
            valido = false;
        }

        if (!regexCEP.test(cep)) {
            mensagemErro += "O <b>CEP</b> deve conter 8 dígitos.<br>";
            valido = false;
        }

        if (!regexTelefone.test(telefone)) {
            mensagemErro += "O <b>Telefone</b> informado é inválido.<br>";
            valido = false;
        }

        // Se encontrou erro, mostra o SweetAlert
        if (!valido) {
            Swal.fire({
                icon: 'error',
                title: 'Ops! Verifique os dados',
                html: mensagemErro,
                confirmButtonColor: '#494949'
            });
            return;
        }

        // Se tudo estiver certo, envia o formulário
        form.submit();
    });
});