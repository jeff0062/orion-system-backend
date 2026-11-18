document.addEventListener('DOMContentLoaded', () => {
    const stockTableBody = document.getElementById('stock-table-body');
    const loadingSpinner = document.getElementById('loading-spinner');
    const stockTable = document.getElementById('stock-table');
    const noItemsMessage = document.getElementById('no-items-message');
    const userIdSpan = document.getElementById('user-id');
    const logoutButton = document.getElementById('logout-button');
    const addItemButton = document.getElementById('add-item-button');
    const itemModal = document.getElementById('item-modal');
    const itemForm = document.getElementById('item-form');
    const modalTitle = document.getElementById('modal-title');
    const cancelButton = document.getElementById('cancel-button');
    const cancel_categoria = document.getElementById('cancela_categoria');

    const categoriaNomeInput = document.getElementById('categoria-nome');
    const categoriaButton = document.getElementById('adi_categoria');
    const categoriaForm = document.getElementById('categoria-form');
    const categoriaModal = document.getElementById('categoria_modal');

    const itemNameInput = document.getElementById('item-name');
    const itemCategoriaInput = document.getElementById('nome_categoria');
    const itemQuantityInput = document.getElementById('item-quantity');
    const itemPriceInput = document.getElementById('item-price');
    const itemIdInput = document.getElementById('item-id');

    // URLs alinhadas com as rotas reais do backend
    const API_BASE_URL = '/api/estoque';
    const API_LOGOUT_URL = '/api/logout';
    const LOGIN_PAGE_URL = '/';
    const USER_ID_URL = '/api/usuarios/me';
    const API_CATEGORIAS_URL = '/api/categorias';

    const formatDate = (timestamp) => {
        if (!timestamp) return 'N/A';
        const date = new Date(timestamp);
        return date.toLocaleDateString('pt-BR', { day: '2-digit', month: 'short', year: 'numeric' }) +
            ' ' + date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
    };

    const renderStockTable = (items) => {
        stockTableBody.innerHTML = '';

        if (!items || items.length === 0) {
            stockTable.classList.add('hidden');
            noItemsMessage.classList.remove('hidden');
        } else {
            noItemsMessage.classList.add('hidden');
            stockTable.classList.remove('hidden');

            items.sort((a, b) => {
                const nomeA = (a.nome || a.name || '').toLowerCase();
                const nomeB = (b.nome || b.name || '').toLowerCase();
                return nomeA.localeCompare(nomeB);
            });

            items.forEach(item => {
                const idEstoque = item.id_estoque ?? item.id;
                const nome = item.nome ?? item.name ?? '';
                const quantidade = item.quantidade ?? item.quantity ?? 0;
                const preco = item.preco ?? item.price ?? 0;
                const dataAtualizacao = item.data_atualizacao ?? item.updated_at ?? null;
                const categoria = item.categoria ?? '';

                const row = document.createElement('tr');
                row.className = 'hover:bg-[#453b44] transition duration-150';

                row.innerHTML = `
                    <td class="px-6 py-4 whitespace-nowrap font-medium text-[#d8bfa4]">${nome}</td>
                    <td class="px-6 py-4 whitespace-nowrap">${quantidade}</td>
                    <td class="px-6 py-4 whitespace-nowrap">R$ ${parseFloat(preco).toFixed(2).replace('.', ',')}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm">${formatDate(dataAtualizacao)}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                        <button data-id="${idEstoque}" data-name="${nome}" data-quantity="${quantidade}" data-price="${preco}" data-categoria="${categoria}" class="edit-btn text-gold hover:text-yellow-400 transition">
                            <span class="material-icons text-lg">edit</span>
                        </button>
                        <button data-id="${idEstoque}" class="delete-btn text-red-600 hover:text-red-400 transition">
                            <span class="material-icons text-lg">delete</span>
                        </button>
                    </td>
                `;
                stockTableBody.appendChild(row);
            });
        }
        loadingSpinner.classList.add('hidden');

        document.querySelectorAll('.edit-btn').forEach(button => {
            button.addEventListener('click', handleEditItem);
        });
        document.querySelectorAll('.delete-btn').forEach(button => {
            button.addEventListener('click', handleDeleteItem);
        });
    };

    const getUserIdFromSession = async () => {
        try {
            const response = await fetch(USER_ID_URL, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
            });
            if (response.status === 401) {
                window.location.href = LOGIN_PAGE_URL;
                return;
            }
            if (response.ok) {
                const data = await response.json();
                if (data.data && data.data.nome) {
                    userIdSpan.textContent = `${data.data.nome} (ID: ${data.data.id_usuario})`;
                } else if (data.data && data.data.id_usuario) {
                    userIdSpan.textContent = String(data.data.id_usuario);
                } else {
                    userIdSpan.textContent = 'Não disponível';
                }
            } else {
                userIdSpan.textContent = 'Não disponível';
            }
        } catch (error) {
            userIdSpan.textContent = 'Erro de rede';
        }
    };

    const fetchStock = async () => {
        loadingSpinner.classList.remove('hidden');
        try {
            const response = await fetch(API_BASE_URL, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
            });

            if (response.status === 401) {
                window.location.href = LOGIN_PAGE_URL;
                return;
            }

            if (!response.ok) {
                throw new Error();
            }

            const responseData = await response.json();
            renderStockTable(responseData.data || []);
        } catch (e) {
            loadingSpinner.innerHTML = `<p class="text-red-500 mt-4 text-lg">Erro ao carregar o estoque. Verifique se o servidor Flask está rodando e o banco conectado.</p>`;
        }
    };

    const saveItem = async (data) => {
        const isEditing = !!data.id;
        const url = isEditing ? `${API_BASE_URL}/${data.id}` : API_BASE_URL;
        const method = isEditing ? 'PUT' : 'POST';

        try {
            const response = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (response.status === 401) {
                window.location.href = LOGIN_PAGE_URL;
                return;
            }

            const result = await response.json();
            if (!response.ok) {
                throw new Error(result.message || 'Erro ao salvar item');
            }

            hideModal();
            fetchStock();
        } catch (e) {
            alert(`Falha ao salvar o item: ${e.message}`);
        }
    };

    const deleteItem = async (itemId) => {
        try {
            const response = await fetch(`${API_BASE_URL}/${itemId}`, {
                method: 'DELETE',
            });

            if (response.status === 401) {
                window.location.href = LOGIN_PAGE_URL;
                return;
            }

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Erro ao excluir');
            }

            fetchStock();
        } catch (e) {
            alert(`Falha ao deletar o item: ${e.message}`);
        }
    };

    const showModal = (title, item = {}) => {
        modalTitle.textContent = title;
        itemIdInput.value = item.id || '';
        itemNameInput.value = item.name || '';
        if (itemCategoriaInput) {
            itemCategoriaInput.value = item.categoria || '';
        }
        itemQuantityInput.value = (item.quantity !== undefined && item.quantity !== '') ? item.quantity : '';
        itemPriceInput.value = (item.price !== undefined && item.price !== '') ? parseFloat(item.price).toFixed(2) : '';
        itemModal.classList.remove('hidden');
    };

    const hideModal = () => {
        itemModal.classList.add('hidden');
        itemForm.reset();
        itemIdInput.value = '';
    };

    const hideModal1 = () => {
        categoriaModal.classList.add('hidden');
        categoriaForm.reset();
    };

    addItemButton.addEventListener('click', () => showModal('Adicionar Novo Item'));

    categoriaButton.addEventListener('click', () => {
        categoriaModal.classList.remove('hidden');
    });

    cancelButton.addEventListener('click', hideModal);
    itemModal.addEventListener('click', (e) => {
        if (e.target.id === 'item-modal') {
            hideModal();
        }
    });

    cancel_categoria.addEventListener('click', hideModal1);
    categoriaModal.addEventListener('click', (e) => {
        if (e.target.id === 'categoria_modal') {
            hideModal1();
        }
    });

    categoriaForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const dados = {
            categoria: categoriaNomeInput.value.trim()
        };

        if (!dados.categoria) {
            alert('Digite o nome da categoria.');
            return;
        }

        try {
            const response = await fetch(API_CATEGORIAS_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(dados)
            });

            const resultado = await response.json();

            if (!response.ok) {
                alert(resultado.message);
                return;
            }

            alert(resultado.message);
            categoriaForm.reset();
            categoriaModal.classList.add('hidden');

        } catch {
            alert('Erro de conexão ao salvar categoria');
        }
    });

    // Submissão do formulário de item (Novo / Edição)
    itemForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const nome = itemNameInput.value.trim();
        const categoriaDigitada = itemCategoriaInput ? itemCategoriaInput.value.trim() : '';
        const quantidade = parseInt(itemQuantityInput.value, 10);
        const preco = parseFloat(itemPriceInput.value);
        const idEstoque = itemIdInput.value;

        if (!nome) {
            alert('Por favor, informe o nome do item.');
            return;
        }

        if (!categoriaDigitada) {
            alert('Por favor, informe a categoria do item.');
            return;
        }

        try {
            // Resolver id_categoria a partir do nome informado
            let idCategoria = null;
            const resCat = await fetch(API_CATEGORIAS_URL);
            if (resCat.ok) {
                const dataCat = await resCat.json();
                const encontrada = (dataCat.data || []).find(
                    c => c.categoria.toLowerCase() === categoriaDigitada.toLowerCase()
                );
                if (encontrada) {
                    idCategoria = encontrada.id_categoria;
                }
            }

            // Se a categoria ainda não existe, cria automaticamente
            if (!idCategoria) {
                const resNovaCat = await fetch(API_CATEGORIAS_URL, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ categoria: categoriaDigitada })
                });
                if (resNovaCat.ok) {
                    const dataNovaCat = await resNovaCat.json();
                    idCategoria = dataNovaCat.data.id_categoria;
                } else {
                    const errCat = await resNovaCat.json();
                    alert(errCat.message || 'Erro ao criar categoria.');
                    return;
                }
            }

            const payload = {
                id: idEstoque || undefined,
                nome: nome,
                quantidade: quantidade,
                preco: preco,
                id_categoria: idCategoria
            };

            await saveItem(payload);

        } catch (err) {
            alert('Erro ao processar item: ' + err.message);
        }
    });

    const handleEditItem = (e) => {
        const btn = e.currentTarget;
        showModal('Editar Item', {
            id: btn.dataset.id,
            name: btn.dataset.name,
            categoria: btn.dataset.categoria || '',
            quantity: parseInt(btn.dataset.quantity, 10),
            price: parseFloat(btn.dataset.price),
        });
    };

    const handleDeleteItem = (e) => {
        const itemId = e.currentTarget.dataset.id;

        if (confirm("Tem certeza que deseja deletar este item do estoque?")) {
            deleteItem(itemId);
        }
    };

    logoutButton.addEventListener('click', async () => {
        try {
            const response = await fetch(API_LOGOUT_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
            });

            if (response.ok) {
                window.location.href = LOGIN_PAGE_URL;
            } else {
                alert("Erro ao fazer logout.");
            }
        } catch (e) {
            window.location.href = LOGIN_PAGE_URL;
        }
    });

    // Inicialização da página
    getUserIdFromSession();
    fetchStock();
});
