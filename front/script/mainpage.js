const productSlideIndices = {};

// Função para mover fotos INTERNAS do produto (Não precisa alterar, as porcentagens já são responsivas)
function moveInternalSlide(productId, step) {
    if (!(productId in productSlideIndices)) {
        productSlideIndices[productId] = 0;
    }

    const container = document.getElementById(`slides-${productId}`);
    if (!container) return;

    const totalImages = container.children.length;
    productSlideIndices[productId] = (productSlideIndices[productId] + step + totalImages) % totalImages;
    
    const offset = productSlideIndices[productId] * 100;
    container.style.transform = `translateX(-${offset}%)`;
}

// Lógica do Carrossel PRINCIPAL
document.addEventListener('DOMContentLoaded', () => {
    // CORREÇÃO: Pegando o ID correto que está no HTML ('carouselTrack')
    const track = document.getElementById('carouselTrack'); 
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const carouselContainer = document.querySelector('.carousel-container');

    if (!track || track.children.length === 0) return;

    let currentPosition = 0;
    const gap = 20; // O gap continua fixo em 20px de acordo com o seu CSS

    // Função que calcula as larguras na hora do clique
    function getCarouselMetrics() {
        const cardWidth = track.children[0].offsetWidth; // Pega a largura real do card na tela atual
        const containerWidth = carouselContainer.offsetWidth; // Pega a largura real do container
        const totalCards = track.children.length;
        const moveAmount = cardWidth + gap; 
        
        // Refaz o cálculo de limite dinamicamente
        const maxScroll = -Math.max(0, (totalCards * moveAmount) - gap - containerWidth);
        
        return { moveAmount, maxScroll };
    }

    nextBtn.addEventListener('click', () => {
        const { moveAmount, maxScroll } = getCarouselMetrics();
        currentPosition = Math.max(currentPosition - moveAmount, maxScroll);
        track.style.transform = `translateX(${currentPosition}px)`;
    });

    prevBtn.addEventListener('click', () => {
        const { moveAmount } = getCarouselMetrics();
        currentPosition = Math.min(currentPosition + moveAmount, 0);
        track.style.transform = `translateX(${currentPosition}px)`;
    });

    // Zera a posição do carrossel caso o usuário gire o celular ou mude o tamanho da janela do navegador
    window.addEventListener('resize', () => {
        currentPosition = 0;
        track.style.transform = `translateX(0px)`;
    });
});