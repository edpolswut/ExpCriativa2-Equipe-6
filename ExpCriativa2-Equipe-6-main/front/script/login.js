document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("formulario");

    form.addEventListener("submit", function (event) {
        event.preventDefault();

        let email = document.getElementById("email").value.trim();
        let senha = document.getElementById("senha").value.trim();

        let valido = true;

        // limpar erros
        document.getElementById("erro-email").textContent = "";
        document.getElementById("erro-senha").textContent = "";

        // valida email
        if (email === "") {
            document.getElementById("erro-email").textContent = "Email obrigatório.";
            valido = false;
        }

        // valida senha
        if (senha === "") {
            document.getElementById("erro-senha").textContent = "Senha obrigatória.";
            valido = false;
        }

        if (!valido) {
            return;
        }

        form.submit();
    });

});