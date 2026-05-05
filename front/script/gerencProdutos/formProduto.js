document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("formularioProduto");

    form.addEventListener("submit", function (event) {
        event.preventDefault();

        let preco = parseFloat(document.getElementById("Preco").value);
        let estoque = parseInt(document.getElementById("Qtd_Estoque").value);
        let imagens = document.querySelector('input[type="file"]').files;

        let valido = true;
        let mensagemErro = "";

        if (isNaN(preco) || preco <= 0) {
            mensagemErro += "O <b>Preço</b> do produto deve ser maior que zero.<br>";
            valido = false;
        }

        if (isNaN(estoque) || estoque < 0) {
            mensagemErro += "A quantidade em <b>Estoque</b> não pode ser negativa.<br>";
            valido = false;
        }
        
        if (imagens.length > 0) {
            for(let i = 0; i < imagens.length; i++) {
                if(!imagens[i].type.startsWith('image/')) {
                    mensagemErro += "Por favor, selecione apenas arquivos de <b>imagem</b>.<br>";
                    valido = false;
                    break;
                }
            }
        }

        if (!valido) {
            Swal.fire({
                icon: 'error',
                title: 'Atenção',
                html: mensagemErro,
                confirmButtonColor: '#FFD166'
            });
            return;
        }

        form.submit();
    });

});

function marcarParaExclusao(idImagem) {
    if(confirm("A imagem será removida permanentemente ao salvar. Confirmar?")) {
        document.getElementById('img-container-' + idImagem).style.display = 'none';
        
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'ImagensParaDeletar';
        input.value = idImagem;
        
        document.getElementById('formularioProduto').appendChild(input);
    }
}