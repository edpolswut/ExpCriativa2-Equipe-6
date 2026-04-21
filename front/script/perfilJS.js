document.addEventListener("DOMContentLoaded", function () {

    const nomeElemento = document.getElementById("nomeUsuario");
    const avatar = document.getElementById("perfilAvatar");

    const cores = [
        "#FFD166", "#06D6A0", "#118AB2",
        "#EF476F", "#8338EC", "#FF9F1C"
    ];

    if (!nomeElemento || !avatar) return;

    let nome = nomeElemento.dataset.nome;

    if (!nome || nome.trim() === "") {
        nome = nomeElemento.textContent.trim();
    }

    if (nome && nome.length > 0) {
        const inicial = nome.charAt(0).toUpperCase();

        avatar.textContent = inicial;

        const index = inicial.charCodeAt(0) % cores.length;
        avatar.style.backgroundColor = cores[index];
    } else {
        avatar.textContent = "U";
    }

});
