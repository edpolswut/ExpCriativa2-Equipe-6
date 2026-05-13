// document.addEventListener("DOMContentLoaded", function () {

//     const nomeElemento = document.getElementById("nomeUsuario");
//     const avatar = document.getElementById("perfilAvatar");

//     const cores = [
//         "#FFD166", "#06D6A0", "#118AB2",
//         "#EF476F", "#8338EC", "#FF9F1C"
//     ];

//     if (!nomeElemento || !avatar) return;

//     let nome = nomeElemento.dataset.nome;

//     if (!nome || nome.trim() === "") {
//         nome = nomeElemento.textContent.trim();
//     }

//     if (nome && nome.length > 0) {
//         const inicial = nome.charAt(0).toUpperCase();

//         avatar.textContent = inicial;

//         const index = inicial.charCodeAt(0) % cores.length;
//         avatar.style.backgroundColor = cores[index];
//     } else {
//         avatar.textContent = "U";
//     }

// });

function toggleEdicaoPerfil() {
    const form = document.getElementById('form-edicao-perfil');
    const cameraIcon = document.getElementById('cameraIcon');
    
    if (form.style.display === "none") {
        form.style.display = "block";
        cameraIcon.style.display = "flex";
    } else {
        form.style.display = "none";
        cameraIcon.style.display = "none";
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

function previewImagem(event) {
    const input = event.target;
    
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            const avatarContainer = document.getElementById('perfilAvatar');
            
            avatarContainer.innerHTML = `
                <img id="previewAvatar" src="${e.target.result}" 
                     style="border-radius: 50%; object-fit: cover; width: 100%; height: 100%;">
            `;
            
            document.getElementById('form-edicao-perfil').style.display = 'block';
            document.getElementById('cameraIcon').style.display = 'flex';
        }
        
        reader.readAsDataURL(input.files[0]);
    }
}