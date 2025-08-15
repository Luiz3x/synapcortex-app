// =================================================================================
// SYNAPCORTEX - LÓGICA DO PAINEL E MODAIS (v4.3 - CORREÇÃO DE SCROLL)
// =================================================================================

document.addEventListener('DOMContentLoaded', function() {
    // --- LÓGICA DO SELETOR 'PRESENTE SURPRESA' ---
    const abandonoTipoSelect = document.getElementById('abandono-tipo-select');
    if (abandonoTipoSelect) {
        // ... (código inalterado) ...
    }

    // --- LÓGICA DOS MODAIS (COM TRAVA DE SCROLL) ---
    function setupModal(modalId, openBtnId) {
        const modal = document.getElementById(modalId);
        const openBtn = document.getElementById(openBtnId);

        if (!modal) return;

        const closeBtn = modal.querySelector('.close-button');

        function openModal() {
            modal.style.display = 'block';
            document.body.classList.add('modal-open'); // ADICIONADO: Trava o scroll do fundo
        }

        function closeModal() {
            modal.style.display = 'none';
            document.body.classList.remove('modal-open'); // ADICIONADO: Destrava o scroll do fundo
        }

        if (openBtn) {
            openBtn.addEventListener('click', openModal);
        }

        if (closeBtn) {
            closeBtn.addEventListener('click', closeModal);
        }

        window.addEventListener('click', (event) => {
            if (event.target == modal) {
                closeModal();
            }
        });
        
        return { openModal, closeModal };
    }

    // Configura o modal de Login/Registro
    setupModal('loginRegisterModal', 'openLoginRegisterModal');
    
    // Configura o modal de Ajuda (lógica movida para dentro da função genérica)
    const helpModal = document.getElementById('helpModal');
    if(helpModal) {
        const platformButtons = document.querySelectorAll('.platform-button');
        const modalTitle = document.getElementById('helpModalTitle');
        const modalContent = document.getElementById('helpModalContent');
        
        platformButtons.forEach(button => {
            button.addEventListener('click', () => {
                const platform = button.dataset.platform;
                modalTitle.textContent = helpData[platform].title;
                modalContent.innerHTML = helpData[platform].content;
                document.body.classList.add('modal-open'); // ADICIONADO: Trava o scroll do fundo
                helpModal.style.display = 'block';
            });
        });
        
        const closeHelpBtn = helpModal.querySelector('.close-button');
        if (closeHelpBtn) {
            closeHelpBtn.addEventListener('click', () => {
                document.body.classList.remove('modal-open'); // ADICIONADO: Destrava o scroll
                helpModal.style.display = 'none';
            });
        }
    }


    // Lógica das abas do modal de Login/Registro
    const tabButtons = document.querySelectorAll('.tab-button');
    // ... (resto da lógica das abas continua igual) ...
    
    // Lógica do botão TEST DRIVE
    const demoLoginBtn = document.getElementById('demoLoginBtn');
    // ... (resto da lógica do test drive continua igual) ...

    // Lógica do formulário de salvar configurações
    const configForm = document.getElementById('config-form');
    // ... (resto da lógica de salvar continua igual) ...

    // Lógica do botão de copiar
    const copiarBtn = document.getElementById('copiar-codigo-btn');
    // ... (resto da lógica de copiar continua igual) ...

    // Conteúdo da Central de Ajuda
    const helpData = { /* ... (objeto helpData continua igual) ... */ };
});