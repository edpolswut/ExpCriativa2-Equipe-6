
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

// Função para carregar o footer
function carregarFooter() {
    fetch('footer.html')
        .then(response => response.text())
        .then(data => {
            document.getElementById('footer-container').innerHTML = data;
        })
        .catch(error => console.error('Erro ao carregar o footer:', error));
}

// Executa a função quando a página terminar de carregar
document.addEventListener('DOMContentLoaded', carregarFooter);
