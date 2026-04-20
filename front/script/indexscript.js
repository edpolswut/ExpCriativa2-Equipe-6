const track = document.getElementById("track");
const next = document.getElementById("next");
const prev = document.getElementById("prev");

let index = 0;

// DUPLICA TODOS OS CARDS
const originalCards = Array.from(track.children);
originalCards.forEach(card => {
    const clone = card.cloneNode(true);
    track.appendChild(clone);
});

function getCardWidth() {
    const card = document.querySelector(".card");
    const style = window.getComputedStyle(track);
    const gap = parseInt(style.gap) || 0;
    return card.offsetWidth + gap;
}

// MOVE
function updateCarousel() {
    track.style.transform = `translateX(-${getCardWidth() * index}px)`;
}

// NEXT
next.addEventListener("click", () => {
    index++;
    track.style.transition = "transform 0.4s ease";
    updateCarousel();

    // RESET INVISÍVEL
    if (index >= originalCards.length) {
        setTimeout(() => {
            track.style.transition = "none";
            index = 0;
            updateCarousel();
        }, 400);
    }
});

// PREV
prev.addEventListener("click", () => {
    if (index <= 0) {
        track.style.transition = "none";
        index = originalCards.length;
        updateCarousel();
    }

    setTimeout(() => {
        index--;
        track.style.transition = "transform 0.4s ease";
        updateCarousel();
    }, 10);
});

// RESPONSIVO
window.addEventListener("resize", () => {
    track.style.transition = "none";
    updateCarousel();
});