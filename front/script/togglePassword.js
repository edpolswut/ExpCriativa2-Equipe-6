// Função reutilizável para toggle de visualização de senha
function inicializarToggleSenha() {
    const botoesSenha = document.querySelectorAll(".toggle-senha");
    
    botoesSenha.forEach(function (botao) {
        botao.addEventListener("click", function (e) {
            e.preventDefault();
            const targetId = botao.getAttribute("data-target");
            const input = document.getElementById(targetId);
            const icon = botao.querySelector("i");

            if (input.type === "password") {
                input.type = "text";
                icon.classList.replace("fa-eye", "fa-eye-slash");
            } else {
                input.type = "password";
                icon.classList.replace("fa-eye-slash", "fa-eye");
            }
        });
    });
}

// Inicializa imediatamente se o DOM estiver pronto
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", inicializarToggleSenha);
} else {
    inicializarToggleSenha();
}
