// --- Lógica do Filtro Acordeão
function toggleFilter(headerElement) {
    const content = headerElement.nextElementSibling;
    const icon = headerElement.querySelector('.toggle-icon');

    if (content.style.display === "none") {
        content.style.display = "flex";
        icon.textContent = "-";
    } else {
        content.style.display = "none";
        icon.textContent = "+";
    }
}

// --- Lógica do Carrossel
const track = document.getElementById('track');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');

const cardWidth = 300; 
const gap = 20;
const moveAmount = cardWidth + gap; 

let currentPosition = 0;

const totalCards = track.children.length;
const containerWidth = 940; 
const maxScroll = -((totalCards * moveAmount) - gap - containerWidth);

nextBtn.addEventListener('click', () => {
    if (currentPosition - moveAmount >= maxScroll) {
        currentPosition -= moveAmount;
    } else {
        currentPosition = maxScroll; 
    }
    track.style.transform = `translateX(${currentPosition}px)`;
});

prevBtn.addEventListener('click', () => {
    if (currentPosition + moveAmount <= 0) {
        currentPosition += moveAmount;
    } else {
        currentPosition = 0;
    }
    track.style.transform = `translateX(${currentPosition}px)`;
});