document.addEventListener('DOMContentLoaded', () => {
    fetch('/get_products')
        .then(response => response.json())
        .then(data => {
            products = data.map(product => ({
                id: product[0],  // Usando o rowid do banco de dados
                name: product[1],
                quantity: product[2]
            }));
            updateProductList();
        });
});

// Lista para armazenar produtos
let products = [];

// Referências aos elementos do DOM
const productForm = document.getElementById('productForm');
const productNameInput = document.getElementById('productName');
const productQuantityInput = document.getElementById('productQuantity');
const productList = document.getElementById('productList');

// Prevenir números negativos ou zero no campo de quantidade
productQuantityInput.addEventListener('input', (event) => {
    const input = event.target;
    if (input.value < 1) {
        input.value = ''; // Limpa o valor se for menor que 1
    }
});

// Função para atualizar a lista de produtos
function updateProductList() {
    productList.innerHTML = ''; // Limpa a lista

    products.forEach((product, index) => {
        const li = document.createElement('li'); // Cria um novo item da lista

        // Verifica se o estoque está vazio
        const stockInfo = product.quantity === 0 
            ? `<span class="out-of-stock">Sem estoque</span> <button class="btn-delete" onclick="deleteProduct(${product.id})"><img src="../static/trash-icon.svg" alt="Excluir"></button>` 
            : `Quantidade: ${product.quantity}`;

        li.innerHTML = `
            <div class="button-group">
                <button class="btn btn-entry" onclick="changeQuantity(${product.id}, 1)">Entrada</button>
                <button class="btn btn-exit" onclick="changeQuantity(${product.id}, -1)">Saída</button>
                <span class="product-info">${product.name}: ${stockInfo}</span>
            </div>
        `;

        productList.appendChild(li); // Adiciona o item à lista
    });
}

// Função para remover um produto da lista
function deleteProduct(productId) {
    fetch(`/delete_product/${productId}`, {
        method: 'DELETE'
    }).then(() => {
        products = products.filter(product => product.id !== productId);
        updateProductList();
    });
}

// Modifica a quantidade de um produto
function changeQuantity(productId, delta) {
    fetch(`/update_quantity/${productId}/${delta}`, {
        method: 'POST'
    }).then(() => {
        const product = products.find(product => product.id === productId);
        product.quantity += delta;
        if (product.quantity < 0) product.quantity = 0; // Não permitir quantidade negativa
        updateProductList();
    });
}