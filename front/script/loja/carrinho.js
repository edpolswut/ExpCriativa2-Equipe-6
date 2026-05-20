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
    }
});

// Intercepta a finalização de compra para mostrar as modais fakes
document.addEventListener("DOMContentLoaded", function() {
    const formCheckout = document.getElementById("form-checkout");
    
    if (formCheckout) {
        formCheckout.addEventListener("submit", function(e) {
            console.log("Form submission attempted. Default prevented.");
            e.preventDefault();
            
            const metodo = document.querySelector('input[name="metodo_pagamento"]:checked').value;

            if (metodo === 'pix') {
                let timerInterval;
                console.log("Initiating PIX SweetAlert.");
                Swal.fire({
                    title: 'Pagamento via PIX',
                    html: `
                        <div style="text-align: center;">
                            <p>Escaneie o QR Code abaixo para pagar:</p>
                            <img src="/front/icons/qrcode.png" style="width: 200px; margin: 15px auto; display: block;" onerror="this.src='https://via.placeholder.com/200?text=QR+CODE'">
                            <p>O código expira em: <strong>5:00</strong></p>
                        </div>
                    `,
                    timer: 300000,
                    timerProgressBar: true,
                    showConfirmButton: true,
                    confirmButtonText: 'Confirmar Pagamento',
                    confirmButtonColor: '#1a9e1a',
                    didOpen: () => {
                        const timerElement = Swal.getHtmlContainer().querySelector('strong');
                        timerInterval = setInterval(() => {
                            const ms = Swal.getTimerLeft();
                            const min = Math.floor(ms / 60000);
                            const sec = Math.floor((ms % 60000) / 1000);
                            timerElement.textContent = `${min}:${sec < 10 ? '0' : ''}${sec}`;
                        }, 1000);
                    },
                    willClose: () => {
                        clearInterval(timerInterval);
                    }
                }).then((result) => {
                    if (result.isConfirmed || result.dismiss === Swal.DismissReason.timer) {
                        console.log("PIX SweetAlert dismissed. Submitting form.");
                        formCheckout.submit();
                    }
                });
            } else if (metodo === 'cartao') {
                console.log("Initiating Cartão SweetAlert.");
                Swal.fire({
                    title: 'Processando Pagamento',
                    text: 'Aguarde enquanto validamos os dados do cartão...',
                    allowOutsideClick: false,
                    didOpen: () => {
                        Swal.showLoading();
                        setTimeout(() => {
                            Swal.fire({
                                icon: 'success',
                                title: 'Pagamento Aprovado!',
                                text: 'Sua compra foi concluída com sucesso.',
                                confirmButtonColor: '#1a9e1a'
                            }).then(() => { // This then block is for the "Pagamento Aprovado!" Swal
                            }).then(() => {
                                formCheckout.submit();
                            });
                        }, 2500);
                    }
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