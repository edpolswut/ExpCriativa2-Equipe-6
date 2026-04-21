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

function toggleEdicaoPerfil() {
    const form = document.getElementById('form-edicao-perfil');
    
    if (form.style.display === "none") {
        form.style.display = "block";
    } else {
        form.style.display = "none";
    }
}

function confirmarExclusao() {
    Swal.fire({
        title: 'Excluir conta?',
        text: "Todas as suas lojas serão desativadas imediatamente!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sim, excluir!',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            window.location.href = "/DeletarUsuario";
        }
    });
}