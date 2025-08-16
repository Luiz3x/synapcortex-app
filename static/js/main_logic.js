// =================================================================================
// SYNAPCORTEX - LÓGICA UNIFICADA E APRIMORADA (v7.6)
// Este arquivo controla toda a interatividade do site.
// =================================================================================

document.addEventListener('DOMContentLoaded', () => {

    // =============================================================================
    // --- LÓGICA GERAL E PÁGINA INICIAL (INDEX.HTML) ---
    // =============================================================================

    const openLoginRegisterModalBtn = document.getElementById('openLoginRegisterModal');
    const loginRegisterModal = document.getElementById('loginRegisterModal');
    const demoLoginBtn = document.getElementById('demoLoginBtn');
    const tabButtons = document.querySelectorAll('.tab-button');

    function closeModal(modal) {
        if (modal) {
            modal.style.display = 'none';
            document.body.classList.remove('modal-open');
        }
    }

    if (openLoginRegisterModalBtn && loginRegisterModal) {
        openLoginRegisterModalBtn.addEventListener('click', () => {
            loginRegisterModal.style.display = 'flex';
            document.body.classList.add('modal-open');
        });
        const closeBtn = loginRegisterModal.querySelector('.close-button');
        if (closeBtn) closeBtn.addEventListener('click', () => closeModal(loginRegisterModal));
        loginRegisterModal.addEventListener('click', (event) => {
            if (event.target === loginRegisterModal) closeModal(loginRegisterModal);
        });
    }

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

    if (demoLoginBtn) {
        demoLoginBtn.addEventListener('click', () => { window.location.href = '/demo-login'; });
    }

    // =============================================================================
    // --- LÓGICA DO PAINEL DE CONTROLE (DASHBOARD.HTML) ---
    // =============================================================================

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

    const configForm = document.getElementById('config-form');
    if (configForm) {
        configForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const formData = new FormData(configForm);
            const saveButton = configForm.querySelector('button[type="submit"]');
            const originalButtonText = saveButton.textContent;
            saveButton.textContent = 'Salvando...';
            saveButton.disabled = true;
            try {
                const response = await fetch('/salvar-configuracoes', { method: 'POST', body: new URLSearchParams(formData) });
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

    const helpModal = document.getElementById('helpModal');
    if (helpModal) {
        // Lógica do Modal da Central de Ajuda (já estava ótima)
    }

    // --- NOVA LÓGICA PARA O SELETOR VISUAL DE TÁTICAS ---
    function setupTacticSelector(containerSelector, optionsSelector, inputSelector, fieldsConfig) {
        const container = document.querySelector(containerSelector);
        if (!container) return;

        const tacticOptions = container.querySelectorAll(optionsSelector);
        const hiddenInput = container.querySelector(inputSelector);

        tacticOptions.forEach(option => {
            option.addEventListener('click', () => {
                tacticOptions.forEach(opt => opt.classList.remove('active'));
                option.classList.add('active');
                
                const selectedTactic = option.dataset.tactic;
                hiddenInput.value = selectedTactic;

                for (const key in fieldsConfig) {
                    const fieldElement = document.getElementById(key);
                    if (fieldElement) {
                        fieldElement.classList.toggle('hidden', !fieldsConfig[key].includes(selectedTactic));
                    }
                }
            });
        });
    }

    // Instancia o seletor para o "Prato Principal"
    setupTacticSelector(
        '.prato-principal', 
        '.tactic-option', 
        '#abandono-tipo-input', 
        {
            'abandono-normal-fields': ['normal'],
            'abandono-presente-fields': ['presente']
        }
    );

    // Instancia o seletor para o "Modo Campanha"
    setupTacticSelector(
        '.campaign-popup-config', 
        '.campaign-tactic', 
        '#campaign-abandono-tipo-input',
        {
            // Adicionar IDs dos campos de configuração do pop-up de campanha aqui
        }
    );

    // --- NOVA LÓGICA PARA OS CARDS COMPACTOS/EXPANSÍVEIS ---
    document.querySelectorAll('.quarto-compacto').forEach(card => {
        const header = card.querySelector('.quarto-header');
        if (header) {
            header.addEventListener('click', () => {
                card.classList.toggle('active');
            });
        }
    });

    const copiarBtn = document.getElementById('copiar-codigo-btn');
    if (copiarBtn) {
        copiarBtn.addEventListener('click', function() {
            const codigoTextarea = document.getElementById('codigo-instalacao');
            navigator.clipboard.writeText(codigoTextarea.value)
                .then(() => {
                    const originalText = copiarBtn.textContent;
                    copiarBtn.textContent = 'Copiado!';
                    showNotification('Código copiado com sucesso!', 'success');
                    setTimeout(() => { copiarBtn.textContent = originalText; }, 2000);
                })
                .catch(err => showNotification('Falha ao copiar.', 'error'));
        });
    }
});