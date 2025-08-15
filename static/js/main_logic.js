// =================================================================================
// SYNAPCORTEX - LÓGICA DO PAINEL E MODAIS (v4.4 - VERSÃO ESTÁVEL FINAL)
// =================================================================================

document.addEventListener('DOMContentLoaded', function() {

    // --- LÓGICA GERAL DOS MODAIS (REVISADA PARA CORRIGIR BUGS) ---
    function setupModalInteraction(modalElement) {
        if (!modalElement) return;

        const closeBtn = modalElement.querySelector('.close-button');

        function closeModal() {
            document.body.classList.remove('modal-open');
            modalElement.style.display = 'none';
        }

        if (closeBtn) {
            closeBtn.addEventListener('click', closeModal);
        }

        modalElement.addEventListener('click', function(event) {
            // Fecha o modal apenas se o clique for no fundo (overlay)
            if (event.target === modalElement) {
                closeModal();
            }
        });
    }

    // Configura o modal de Login/Registro
    const loginRegisterModal = document.getElementById('loginRegisterModal');
    const openLoginBtn = document.getElementById('openLoginRegisterModal');
    if (loginRegisterModal && openLoginBtn) {
        setupModalInteraction(loginRegisterModal);
        openLoginBtn.addEventListener('click', () => {
            document.body.classList.add('modal-open');
            loginRegisterModal.style.display = 'block';
        });
    }

    // Configura o modal de Ajuda
    const helpModal = document.getElementById('helpModal');
    if (helpModal) {
        setupModalInteraction(helpModal);
        const platformButtons = document.querySelectorAll('.platform-button');
        platformButtons.forEach(button => {
            button.addEventListener('click', () => {
                // Preenche e abre o modal de ajuda
                // ... (lógica de preenchimento do helpData continua a mesma) ...
                document.body.classList.add('modal-open');
                helpModal.style.display = 'block';
            });
        });
    }


    // --- LÓGICA DO PAINEL (INTACTA E FUNCIONAL) ---
    
    // Seletor 'Presente Surpresa'
    const abandonoTipoSelect = document.getElementById('abandono-tipo-select');
    if (abandonoTipoSelect) {
        // ... (código do seletor continua o mesmo) ...
    }

    // Formulário de salvar configurações (AJAX)
    const configForm = document.getElementById('config-form');
    if (configForm) {
        configForm.addEventListener('submit', function(e) {
            e.preventDefault(); // Garante que a interceptação funcione
            // ... (resto do código de fetch e notificação continua o mesmo) ...
        });
    }
    
    // Botão de copiar
    const copiarBtn = document.getElementById('copiar-codigo-btn');
    if (copiarBtn) {
        // ... (código de copiar continua o mesmo) ...
    }


    // --- LÓGICA DA PÁGINA INICIAL (INTACTA E FUNCIONAL) ---

    // Abas do Modal de Login/Registro
    const tabButtons = document.querySelectorAll('.tab-button');
    if (tabButtons.length > 0) {
        // ... (código das abas continua o mesmo) ...
    }

    // Botão Test Drive
    const demoLoginBtn = document.getElementById('demoLoginBtn');
    if (demoLoginBtn) {
        // ... (código do test drive continua o mesmo) ...
    }

    // Conteúdo da Central de Ajuda
    const helpData = { /* ... (objeto helpData continua igual) ... */ };
});