// =================================================================================
// SYNAPCORTEX - LÓGICA UNIFICADA (v8.2 - BOTÃO DA CONFIANÇA E GESTÃO DE CONTA)
// =================================================================================

document.addEventListener('DOMContentLoaded', () => {

    // =============================================================================
    // --- LÓGICA GERAL E PÁGINA INICIAL (INDEX.HTML) ---
    // =============================================================================

    const openLoginRegisterModalBtn = document.getElementById('openLoginRegisterModal');
    const loginRegisterModal = document.getElementById('loginRegisterModal');
    const demoLoginBtn = document.getElementById('demoLoginBtn');
    const tabButtons = document.querySelectorAll('.tab-button');
    
    // Função genérica para fechar qualquer modal visível
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
        demoLoginBtn.addEventListener('click', () => { window.location.href = '/demo-login'; });
    }
    
    // Lógica do formulário de registro internacional
    const countrySelect = document.getElementById('country_select');
    if (countrySelect) {
        const companyIdLabel = document.getElementById('company_id_label');
        const companyIdInput = document.getElementById('company_id_input');
        const companyIdConfig = {
            'Brasil': { label: 'CNPJ:', placeholder: '00.000.000/0000-00' },
            'Estados Unidos': { label: 'EIN (Tax ID):', placeholder: '00-0000000' },
            'Portugal': { label: 'NIF / NIPC:', placeholder: '000000000' },
            'Outro': { label: 'ID Fiscal da Empresa:', placeholder: 'Número de registro da sua empresa' }
        };
        countrySelect.addEventListener('change', () => {
            const selectedCountry = countrySelect.value;
            const config = companyIdConfig[selectedCountry] || companyIdConfig['Outro'];
            companyIdLabel.textContent = config.label;
            companyIdInput.placeholder = config.placeholder;
        });
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

    function setupTacticSelector(container, optionsSelector, inputSelector, fieldsConfig) {
        if (!container) return;
        const tacticOptions = container.querySelectorAll(optionsSelector);
        const hiddenInput = container.querySelector(inputSelector);
        if (!tacticOptions.length || !hiddenInput) return;
        tacticOptions.forEach(option => {
            option.addEventListener('click', () => {
                tacticOptions.forEach(opt => opt.classList.remove('active'));
                option.classList.add('active');
                const selectedTacticRaw = option.dataset.tactic;
                const selectedTactic = selectedTacticRaw.replace('campaign-', '');
                hiddenInput.value = selectedTactic;
                for (const key in fieldsConfig) {
                    const fieldElement = document.getElementById(key);
                    if (fieldElement) {
                        fieldElement.classList.toggle('hidden', !fieldsConfig[key].includes(selectedTacticRaw));
                    }
                }
            });
        });
    }
    
    const pratoPrincipalCard = document.querySelector('.prato-principal');
    if(pratoPrincipalCard) {
        setupTacticSelector(pratoPrincipalCard, '.tactic-option', '#abandono-tipo-input', {'abandono-normal-fields': ['normal'], 'abandono-presente-fields': ['presente']});
    }
    const campaignPopupConfig = document.querySelector('.campaign-popup-config');
    if(campaignPopupConfig) {
        setupTacticSelector(campaignPopupConfig, '.campaign-tactic', '#campaign-abandono-tipo-input', {'campaign-normal-fields': ['campaign-normal'], 'campaign-presente-fields': ['campaign-presente']});
    }

    document.querySelectorAll('.quarto-compacto').forEach(card => {
        const header = card.querySelector('.quarto-header');
        if (header) {
            header.addEventListener('click', (e) => {
                if (e.target.closest('.switch')) return;
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

    const changeEmailForm = document.getElementById('change-email-form');
    if (changeEmailForm) {
        changeEmailForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const formData = new FormData(changeEmailForm);
            const saveButton = changeEmailForm.querySelector('button[type="submit"]');
            const originalButtonText = saveButton.textContent;
            saveButton.textContent = 'Salvando...';
            saveButton.disabled = true;
            try {
                const response = await fetch('/mudar-email', { method: 'POST', body: new URLSearchParams(formData) });
                const data = await response.json();
                showNotification(data.message, data.status === 'success' ? 'success' : 'error');
                if (response.ok) {
                    setTimeout(() => window.location.reload(), 2000);
                }
            } catch (error) {
                showNotification('Erro de comunicação.', 'error');
            } finally {
                saveButton.textContent = originalButtonText;
                saveButton.disabled = false;
            }
        });
    }
    
    const cancelarBtn = document.getElementById('cancelar-conta-btn');
    const cancelModal = document.getElementById('cancelModal');
    if (cancelarBtn && cancelModal) {
        const closeButtons = cancelModal.querySelectorAll('[data-close-modal="cancelModal"]');
        const confirmarBtn = document.getElementById('confirmar-cancelamento-btn');
        cancelarBtn.addEventListener('click', () => {
            cancelModal.style.display = 'flex';
            document.body.classList.add('modal-open');
        });
        const closeModalFunc = () => {
            cancelModal.style.display = 'none';
            document.body.classList.remove('modal-open');
        };
        closeButtons.forEach(btn => btn.addEventListener('click', closeModalFunc));
        cancelModal.addEventListener('click', (event) => { if (event.target === cancelModal) closeModalFunc(); });
        confirmarBtn.addEventListener('click', async () => {
            confirmarBtn.textContent = 'Encerrando...';
            confirmarBtn.disabled = true;
            try {
                const response = await fetch('/encerrar-conta', { method: 'POST' });
                const data = await response.json();
                if (data.status === 'success') {
                    window.location.href = data.redirect_url;
                } else {
                    showNotification(data.message || 'Ocorreu um erro.', 'error');
                    confirmarBtn.textContent = 'Sim, encerrar';
                    confirmarBtn.disabled = false;
                }
            } catch (error) {
                showNotification('Erro de comunicação.', 'error');
                confirmarBtn.textContent = 'Sim, encerrar';
                confirmarBtn.disabled = false;
            }
        });
    }
});