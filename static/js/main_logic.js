// =================================================================================
// SYNAPCORTEX - LÓGICA UNIFICADA (INDEX E DASHBOARD) v7.0
// Este arquivo controla toda a interatividade do site.
// =================================================================================

document.addEventListener('DOMContentLoaded', () => {

    // =============================================================================
    // --- LÓGICA DA PÁGINA INICIAL (INDEX.HTML) ---
    // =============================================================================

    const openLoginRegisterModalBtn = document.getElementById('openLoginRegisterModal');
    const loginRegisterModal = document.getElementById('loginRegisterModal');
    const demoLoginBtn = document.getElementById('demoLoginBtn');
    const tabButtons = document.querySelectorAll('.tab-button');

    // Função para fechar qualquer modal aberto
    function closeModal() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.style.display = 'none';
        });
        document.body.classList.remove('modal-open');
    }

    // Abre o modal de Login/Registro
    if (openLoginRegisterModalBtn && loginRegisterModal) {
        openLoginRegisterModalBtn.addEventListener('click', () => {
            loginRegisterModal.style.display = 'flex';
            document.body.classList.add('modal-open');
        });

        // Evento para fechar clicando no 'X' ou fora do conteúdo
        const closeBtn = loginRegisterModal.querySelector('.close-button');
        if (closeBtn) closeBtn.addEventListener('click', closeModal);
        loginRegisterModal.addEventListener('click', (event) => {
            if (event.target === loginRegisterModal) closeModal();
        });
    }

    // Lógica das abas de Login e Registro
    if (tabButtons.length > 0) {
        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                tabButtons.forEach(btn => btn.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
                button.classList.add('active');
                const tabId = button.dataset.tab + 'Tab';
                document.getElementById(tabId).classList.add('active');
            });
        });
    }

    // Botão de Test Drive
    if (demoLoginBtn) {
        demoLoginBtn.addEventListener('click', () => {
            window.location.href = '/demo-login';
        });
    }


    // =============================================================================
    // --- LÓGICA DO PAINEL DE CONTROLE (DASHBOARD.HTML) ---
    // =============================================================================

    const configForm = document.getElementById('config-form');
    const helpModal = document.getElementById('helpModal');
    const copiarBtn = document.getElementById('copiar-codigo-btn');
    const tipoAbandonoSelect = document.getElementById('abandono-tipo-select');

    // Função para criar e exibir notificações
    function showNotification(message, status) {
        const notification = document.createElement('div');
        notification.className = `notification ${status}`;
        notification.textContent = message;
        document.body.appendChild(notification);
        setTimeout(() => notification.classList.add('show'), 10);
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => { if (document.body.contains(notification)) document.body.removeChild(notification); }, 500);
        }, 4000);
    }

    // Lógica para salvar o formulário de configurações
    if (configForm) {
        configForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const formData = new FormData(configForm);
            const saveButton = configForm.querySelector('button[type="submit"]');
            const originalButtonText = saveButton.textContent;
            saveButton.textContent = 'Salvando...';
            saveButton.disabled = true;

            try {
                const response = await fetch('/salvar-configuracoes', {
                    method: 'POST',
                    body: new URLSearchParams(formData)
                });
                if (!response.ok) throw new Error('Erro na resposta do servidor.');
                const data = await response.json();
                showNotification(data.message, data.status);
            } catch (error) {
                console.error('Erro de comunicação:', error);
                showNotification('Erro de comunicação. Tente novamente.', 'error');
            } finally {
                saveButton.textContent = originalButtonText;
                saveButton.disabled = false;
            }
        });
    }

    // Lógica do Modal da Central de Ajuda
    if (helpModal) {
        const helpModalTitle = document.getElementById('helpModalTitle');
        const helpModalContent = document.getElementById('helpModalContent');
        const helpCloseBtn = helpModal.querySelector('.close-button');

        const helpData = {
            shopify: { title: 'Instalando na Shopify', content: `<ol><li>Acesse "Loja Virtual" > "Temas".</li><li>Clique em (...) e "Editar código".</li><li>No arquivo 'theme.liquid', cole o código antes de <code>&lt;/body&gt;</code>.</li><li>Salve.</li></ol>` },
            woocommerce: { title: 'Instalando no WooCommerce', content: `<ol><li>Vá em "Aparência" > "Editor de Arquivos de Tema".</li><li>Encontre e clique em "Rodapé do Tema (footer.php)".</li><li>Cole o código antes de <code>&lt;/body&gt;</code>.</li><li>Atualize o arquivo.</li></ol>` },
            nuvemshop: { title: 'Instalando na Nuvemshop', content: `<ol><li>Vá em "Configurações" > "Códigos externos".</li><li>Cole o código na caixa "No corpo do site".</li><li>Salve.</li></ol>` },
            universal: { title: 'Instalação Universal', content: `<ol><li>Encontre seu arquivo HTML principal.</li><li>Cole o código antes da tag <code>&lt;/body&gt;</code>.</li><li>Salve e publique.</li></ol>` }
        };

        document.querySelectorAll('.platform-button').forEach(button => {
            button.addEventListener('click', function() {
                const platform = this.dataset.platform;
                if (helpData[platform]) {
                    helpModalTitle.textContent = helpData[platform].title;
                    helpModalContent.innerHTML = helpData[platform].content;
                }
                helpModal.style.display = 'flex';
                document.body.classList.add('modal-open');
            });
        });
        
        if(helpCloseBtn) helpCloseBtn.addEventListener('click', () => closeModal(helpModal));
        helpModal.addEventListener('click', (event) => { if (event.target === helpModal) closeModal(helpModal); });
    }

    // Lógica para mostrar/esconder campos do "Presente Surpresa"
    if (tipoAbandonoSelect) {
        const presenteFields = document.getElementById('abandono-presente-fields');
        const normalFields = document.getElementById('abandono-normal-fields');
        const toggleFields = () => {
            const isPresente = tipoAbandonoSelect.value === 'presente';
            presenteFields.classList.toggle('hidden', !isPresente);
            normalFields.classList.toggle('hidden', isPresente);
        };
        tipoAbandonoSelect.addEventListener('change', toggleFields);
        toggleFields();
    }

    // Lógica do botão de copiar código
    if (copiarBtn) {
        copiarBtn.addEventListener('click', function() {
            const codigoTextarea = document.getElementById('codigo-instalacao');
            navigator.clipboard.writeText(codigoTextarea.value)
                .then(() => showNotification('Código copiado com sucesso!', 'success'))
                .catch(err => showNotification('Falha ao copiar.', 'error'));
        });
    }
});