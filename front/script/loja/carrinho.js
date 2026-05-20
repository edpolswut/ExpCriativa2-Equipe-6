// Aguarda o carregamento do HTML para adicionar o evento ao CEP
document.addEventListener("DOMContentLoaded", function() {
    const inputCep = document.getElementById("novo_cep");
    
    if (inputCep) {
        inputCep.addEventListener("blur", function() {
            // Remove tudo o que não for número
            let cepVal = this.value.replace(/\D/g, "");

            if (cepVal.length === 8) {
                // Mostra um feedback visual simples enquanto procura
                document.getElementById("nova_rua").value = "A procurar...";
                document.getElementById("novo_bairro").value = "A procurar...";
                document.getElementById("nova_cidade").value = "A procurar...";

                fetch(`https://viacep.com.br/ws/${cepVal}/json/`)
                    .then(resposta => resposta.json())
                    .then(dados => {
                        if (!dados.erro) {
                            // Preenche os campos automaticamente com base nos IDs do nosso HTML
                            document.getElementById("nova_rua").value = dados.logradouro;
                            document.getElementById("novo_bairro").value = dados.bairro;
                            document.getElementById("nova_cidade").value = dados.localidade; 
                            
                            // Move o foco para o campo "Número" para facilitar a vida do utilizador
                            document.getElementById("novo_numero").focus();
                        } else {
                            // Se o CEP não existir
                            limparCamposEndereco();
                            
                            // Validação caso o SweetAlert (Swal) esteja incluído na página
                            if (typeof Swal !== 'undefined') {
                                Swal.fire({
                                    icon: 'warning',
                                    title: 'CEP não encontrado',
                                    text: 'Verifique se digitou corretamente.',
                                    confirmButtonColor: '#FFD166'
                                });
                            } else {
                                alert("CEP não encontrado. Verifique se digitou corretamente.");
                            }
                        }
                    })
                    .catch(erro => {
                        console.error("Erro na API ViaCEP:", erro);
                        limparCamposEndereco();
                    });
            }
        });
    }
});

function limparCamposEndereco() {
    document.getElementById("nova_rua").value = "";
    document.getElementById("novo_bairro").value = "";
    document.getElementById("nova_cidade").value = "";
}


/* =========================================
   FUNÇÕES DE UI DO CHECKOUT (Carrinho)
   ========================================= */

function toggleNovoEndereco() {
    const form = document.getElementById('novo-endereco-form');
    const radioNovoEnd = document.getElementById('radio-novo-end');
    
    if (form.style.display === 'none' || form.style.display === '') {
        form.style.display = 'block';
        radioNovoEnd.checked = true;
        
        // Torna os campos obrigatórios
        document.getElementById('novo_cep').required = true;
        document.getElementById('nova_rua').required = true;
        document.getElementById('novo_numero').required = true;
        document.getElementById('nova_cidade').required = true;
        document.getElementById('novo_bairro').required = true;
    } else {
        fecharNovoEndereco();
    }
}

function fecharNovoEndereco() {
    const form = document.getElementById('novo-endereco-form');
    form.style.display = 'none';
    
    // Remove a obrigatoriedade
    document.getElementById('novo_cep').required = false;
    document.getElementById('nova_rua').required = false;
    document.getElementById('novo_numero').required = false;
    document.getElementById('nova_cidade').required = false;
    document.getElementById('novo_bairro').required = false;
}

function togglePagamento() {
    const pix = document.getElementById('pagamento-pix').checked;
    const camposCartao = document.getElementById('campos-cartao');
    
    const ccNumero = document.getElementById('cc_numero');
    const ccNome = document.getElementById('cc_nome');
    const ccVal = document.getElementById('cc_validade');
    const ccCvv = document.getElementById('cc_cvv');

    if (pix) {
        camposCartao.style.display = 'none';
        ccNumero.required = false;
        ccNome.required = false;
        ccVal.required = false;
        ccCvv.required = false;
    } else {
        camposCartao.style.display = 'block';
        ccNumero.required = true;
        ccNome.required = true;
        ccVal.required = true;
        ccCvv.required = true;
    }
}