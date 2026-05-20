document.addEventListener('DOMContentLoaded', () => {
    const track = document.getElementById('carouselTrack');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const container = document.getElementById('carouselContainer');
    
    let scrollPosition = 0;

    // Garante que os elementos existem na tela antes de associar os eventos
    if (prevBtn && nextBtn && track && container) {
        
        nextBtn.addEventListener('click', () => {
            const firstCard = track.querySelector('.product-card');
            if (!firstCard) return;

            // Calcula a largura dinâmica do card somando o espaçamento (gap de 20px)
            const cardWidth = firstCard.offsetWidth + 20; 
            const maxScroll = track.scrollWidth - container.offsetWidth;
            
            scrollPosition += cardWidth;
            if (scrollPosition > maxScroll) {
                scrollPosition = maxScroll;
            }
            
            track.style.transform = `translateX(-${scrollPosition}px)`;
        });

        prevBtn.addEventListener('click', () => {
            const firstCard = track.querySelector('.product-card');
            if (!firstCard) return;

            const cardWidth = firstCard.offsetWidth + 20;
            
            scrollPosition -= cardWidth;
            if (scrollPosition < 0) {
                scrollPosition = 0;
            }
            
            track.style.transform = `translateX(-${scrollPosition}px)`;
        });
        
        // Redefine o posicionamento caso a tela mude de tamanho de forma drástica
        window.addEventListener('resize', () => {
            scrollPosition = 0;
            track.style.transform = `translateX(0px)`;
        });
    }
});