document.getElementById("formulario").addEventListener("submit", function(event) {
    event.preventDefault();

    let nome = document.getElementById("Nome").value.trim();
    let email = document.getElementById("Email").value.trim();
    let senha = document.getElementById("Senha").value.trim();

    let valido = true;

    if (nome === "") {
        document.getElementById("erro-nome").textContent = "Nome é obrigatório.";
        valido = false;
    }

    let regexEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (email === "") {
        document.getElementById("erro-email").textContent = "Email é obrigatório.";
        valido = false;
    } else if (!regexEmail.test(email)) {
        document.getElementById("erro-email").textContent = "Email inválido.";
        valido = false;
    }

    if (senha === "") {
        document.getElementById("erro-senha").textContent = "Senha é obrigatória.";
        valido = false;
    } else if (senha.length < 8) {
        document.getElementById("erro-senha").textContent = "Senha deve ter pelo menos 8 caracteres.";
        valido = false;
    }

    // Se tudo estiver válido
    if (valido) {
        alert("Formulário enviado com sucesso!");
        // Aqui você pode enviar para servidor futuramente
        document.getElementById("formulario").submit();
    }
});
