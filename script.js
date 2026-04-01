document.getElementById("formulario").addEventListener("submit", function(event) {
    event.preventDefault();

    let nome = document.getElementById("nome").value.trim();
    let email = document.getElementById("email").value.trim();
    let senha = document.getElementById("senha").value.trim();

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
        document.getElementById("erro-senha").textContent = "Senha deve ter pelo menos 6 caracteres.";
        valido = false;
    }

    // Se tudo estiver válido
    if (valido) {
        alert("Formulário enviado com sucesso!");
        // Aqui você pode enviar para servidor futuramente
        document.getElementById("formulario").submit();
    }
});