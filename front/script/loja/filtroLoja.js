document.addEventListener("DOMContentLoaded", function() {
    // Seletores - Certifique-se de que os IDs coincidem com o seu HTML
    const inputBuscaHeader = document.getElementById("input-pesquisa-header");
    const inputBuscaOculta = document.getElementById("busca-oculta");
    const formFiltros = document.getElementById("form-filtros");
    const elementosFiltro = document.querySelectorAll('#form-filtros input[type="checkbox"], #form-filtros input[type="radio"]');

    // 1. Sincroniza o valor inicial: se já existe uma busca na URL, preenche o campo do header
    if (inputBuscaHeader && inputBuscaOculta && inputBuscaOculta.value) {
        inputBuscaHeader.value = inputBuscaOculta.value;
    }

    // 2. Escuta o 'Enter' na barra de pesquisa do header
    if (inputBuscaHeader && formFiltros) {
        inputBuscaHeader.addEventListener("keypress", function(event) {
            if (event.key === "Enter") {
                event.preventDefault();
                // Copia o que o usuário digitou no header para o campo oculto do formulário de filtros
                inputBuscaOculta.value = this.value;
                formFiltros.submit();
            }
        });
    }

    // 3. Submissão automática ao marcar/desmarcar filtros (Categorias e Preços)
    elementosFiltro.forEach(item => {
        item.addEventListener("change", function() {
            if (formFiltros) {
                // Antes de enviar, garante que o termo atual da busca no header não seja perdido
                if (inputBuscaHeader && inputBuscaOculta) {
                    inputBuscaOculta.value = inputBuscaHeader.value;
                }
                formFiltros.submit();
            }
        });
    });
});