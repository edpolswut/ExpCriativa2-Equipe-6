
function trocarImagem(miniaturaClicada) {
    // 1. Pega a imagem grande pelo ID
    const imagemPrincipal = document.getElementById('imagem-principal');
    
    // 2. Troca o "src" da imagem grande pelo "src" da miniatura que foi clicada
    imagemPrincipal.src = miniaturaClicada.src;

    // 3. Remove a borda azul (classe 'active') de todas as miniaturas
    const todasMiniaturas = document.querySelectorAll('.thumb');
    todasMiniaturas.forEach(thumb => {
        thumb.classList.remove('active');
    });

    // 4. Adiciona a borda azul apenas na miniatura que acabou de ser clicada
    miniaturaClicada.classList.add('active');
}

// Função para adicionar ao carrinho
document.addEventListener('DOMContentLoaded', function() {
    const btnComprar = document.querySelector('.btn-comprar');
    
    if (btnComprar && !btnComprar.disabled) {
        btnComprar.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Pega o identificador da loja do data attribute
            const identificador = this.dataset.identificador;
            
            // Pega o ID do produto da URL
            const pathparts = window.location.pathname.split('/');
            const idProduto = pathparts[pathparts.length - 1];
            
            // Cria um formulário dinamicamente para enviar uma requisição POST
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = `/loja/${identificador}/carrinho/adicionar/${idProduto}`;
            
            // Adiciona o formulário ao corpo do documento e o submete
            document.body.appendChild(form);
            form.submit();
        });
    }
});