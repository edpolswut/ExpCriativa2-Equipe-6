function confirmarExclusao(id) {
    Swal.fire({
        title: 'Deseja excluir este produto?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#494949',
        confirmButtonText: 'Sim, excluir',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            window.location.href = "/DeletarProduto/" + id + "?id_loja=" + document.getElementById('id-loja-hidden').value;
        }
    });
}

function ajustarEstoque(id, nome, estoqueAtual) {
    const html = `
        <form id="form-estoque-ajuste" class="swal2-content" style="display:flex; flex-direction:column; gap:0.75rem;">
            <div>Estoque atual: <strong>${estoqueAtual}</strong> unidades</div>
            <input id="quantidadeEstoque" type="number" min="1" step="1" value="1" class="swal2-input" style="width: 80%;"/>
        </form>
    `;

    Swal.fire({
        title: `Ajustar estoque de ${nome}`,
        html: html,
        showDenyButton: true,
        showCancelButton: true,
        confirmButtonText: 'Adicionar',
        denyButtonText: 'Remover',
        cancelButtonText: 'Cancelar',
        focusConfirm: false,
        didOpen: () => {
            const input = document.getElementById('quantidadeEstoque');
            if (input) {
                input.focus();
                input.select();
            }
        },
        preConfirm: () => {
            const input = document.getElementById('quantidadeEstoque');
            const value = input ? Number(input.value) : NaN;

            if (!value || value <= 0) {
                Swal.showValidationMessage('Informe um valor positivo');
                return false;
            }
            return value;
        },
        preDeny: () => {
            const input = document.getElementById('quantidadeEstoque');
            const value = input ? Number(input.value) : NaN;

            if (!value || value <= 0) {
                Swal.showValidationMessage('Informe um valor positivo');
                return false;
            }
            return value;
        }
    }).then((result) => {
        if (result.isConfirmed || result.isDenied) {
            const quantidade = Number(result.value);
            const ajuste = result.isDenied ? -quantidade : quantidade;

            const form = document.createElement('form');
            form.method = 'post';
            form.action = '/AlterarEstoqueProduto';

            const campoId = document.createElement('input');
            campoId.type = 'hidden';
            campoId.name = 'id_produto';
            campoId.value = id;
            form.appendChild(campoId);

            const campoQtd = document.createElement('input');
            campoQtd.type = 'hidden';
            campoQtd.name = 'qtd_alterar';
            campoQtd.value = ajuste;
            form.appendChild(campoQtd);

            const campoLoja = document.createElement('input');
            campoLoja.type = 'hidden';
            campoLoja.name = 'id_loja';
            campoLoja.value = document.getElementById('id-loja-hidden').value;
            form.appendChild(campoLoja);

            document.body.appendChild(form);
            form.submit();
        }
    });
}
