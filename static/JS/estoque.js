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
        const saveButton = document.getElementById('save-button');
        const cancelButton = document.getElementById('cancel-button');
        
        const itemNameInput = document.getElementById('item-name');
        const itemQuantityInput = document.getElementById('item-quantity');
        const itemPriceInput = document.getElementById('item-price');
        const itemIdInput = document.getElementById('item-id');

        const API_BASE_URL = 'http://127.0.0.1:5000/api/estoque';
        const API_LOGOUT_URL = 'http://127.0.0.1:5000/logout';
        const LOGIN_PAGE_URL = 'http://127.0.0.1:5000/';
        const USER_ID_URL = 'http://127.0.0.1:5000/get_session_id_usuario';

        const formatDate = (timestamp) => {
            if (!timestamp) return 'N/A';
            const date = new Date(timestamp);
            return date.toLocaleDateString('pt-BR', { day: '2-digit', month: 'short', year: 'numeric' }) + 
                   ' ' + date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
        };
        
        const renderStockTable = (items) => {
            stockTableBody.innerHTML = '';
            
            if (items.length === 0) {
                stockTable.classList.add('hidden');
                noItemsMessage.classList.remove('hidden');
            } else {
                noItemsMessage.classList.add('hidden');
                stockTable.classList.remove('hidden');

                items.sort((a, b) => (a.name > b.name) ? 1 : -1);

                items.forEach(item => {
                    const row = document.createElement('tr');
                    row.className = 'hover:bg-[#453b44] transition duration-150';

                    row.innerHTML = `
                        <td class="px-6 py-4 whitespace-nowrap font-medium text-[#d8bfa4]">${item.name}</td>
                        <td class="px-6 py-4 whitespace-nowrap">${item.quantity}</td>
                        <td class="px-6 py-4 whitespace-nowrap">R$ ${item.price ? parseFloat(item.price).toFixed(2).replace('.', ',') : '0,00'}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm">${formatDate(item.updated_at)}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                            <button data-id="${item.id}" data-name="${item.name}" data-quantity="${item.quantity}" data-price="${item.price}" class="edit-btn text-gold hover:text-yellow-400 transition">
                                <span class="material-icons text-lg">edit</span>
                            </button>
                            <button data-id="${item.id}" class="delete-btn text-red-600 hover:text-red-400 transition">
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
                    userIdSpan.textContent = data.user_id || 'Não disponível';
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
                loadingSpinner.innerHTML = `<p class="text-red-500 mt-4 text-lg">Erro ao carregar o estoque. Verifique se o servidor Flask está a correr e se o DB está acessível na porta 5000.</p>`;
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

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.message);
                }
                
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
                    throw new Error(errorData.message);
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
            itemQuantityInput.value = item.quantity || '';
            itemPriceInput.value = item.price ? parseFloat(item.price).toFixed(2) : ''; 
            itemModal.classList.remove('hidden');
        };

        const hideModal = () => {
            itemModal.classList.add('hidden');
            itemForm.reset();
        };

        addItemButton.addEventListener('click', () => showModal('Adicionar Novo Item'));

        cancelButton.addEventListener('click', hideModal);
        itemModal.addEventListener('click', (e) => {
            if (e.target.id === 'item-modal') {
                hideModal();
            }
        });
        
        itemForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const priceValue = parseFloat(itemPriceInput.value); 

            if (isNaN(priceValue) || priceValue < 0) {
                alert("Por favor, insira um preço válido.");
                return;
            }

            const data = {
                id: itemIdInput.value || undefined,
                name: itemNameInput.value.trim(),
                quantity: parseInt(itemQuantityInput.value, 10),
                price: priceValue,
            };
            
            await saveItem(data);
            hideModal();
        });

        const handleEditItem = (e) => {
            const btn = e.currentTarget;
            showModal('Editar Item', {
                id: btn.dataset.id,
                name: btn.dataset.name,
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

        document.addEventListener('DOMContentLoaded', () => {
            getUserIdFromSession();
            fetchStock();
        });
        });
