
const productSlideIndices = {};

// Função para mover fotos INTERNAS do produto
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

// // Lógica do Carrossel PRINCIPAL
// document.addEventListener('DOMContentLoaded', () => {
//     const track = document.getElementById('track');
//     const prevBtn = document.getElementById('prevBtn');
//     const nextBtn = document.getElementById('nextBtn');

//     if (!track || track.children.length === 0) return;

//     const cardWidth = 300; 
//     const gap = 20;
//     const moveAmount = cardWidth + gap; 
//     let currentPosition = 0;

//     const totalCards = track.children.length;
//     const containerWidth = 940; 
//     // Cálculo do limite de scroll para não sobrar espaço em branco
//     const maxScroll = -Math.max(0, (totalCards * moveAmount) - gap - containerWidth);

//     nextBtn.addEventListener('click', () => {
//         currentPosition = Math.max(currentPosition - moveAmount, maxScroll);
//         track.style.transform = `translateX(${currentPosition}px)`;
//     });

//     prevBtn.addEventListener('click', () => {
//         currentPosition = Math.min(currentPosition + moveAmount, 0);
//         track.style.transform = `translateX(${currentPosition}px)`;
//     });
// });