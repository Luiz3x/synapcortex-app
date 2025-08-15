// =================================================================================
// SYNAPCORTEX - LÓGICA DO PAINEL E MODAIS (v6.1 - CORREÇÃO TEST DRIVE)
// =================================================================================

document.addEventListener('DOMContentLoaded', function() {

    // --- LÓGICA GERAL DOS MODAIS ---
    function setupModalInteraction(modalElement, openBtn) {
        if (!modalElement || !openBtn) return;

        const closeBtn = modalElement.querySelector('.close-button');

        function openModal() {
            modalElement.style.display = 'block';
            document.body.classList.add('modal-open');
        }

        function closeModal() {
            modalElement.style.display = 'none';
            document.body.classList.remove('modal-open');
        }

        openBtn.addEventListener('click', openModal);
        if (closeBtn) closeBtn.addEventListener('click', closeModal);
        modalElement.addEventListener('click', function(event) {
            if (event.target === modalElement) closeModal();
        });
    }

    setupModalInteraction(document.getElementById('loginRegisterModal'), document.getElementById('openLoginRegisterModal'));

    // --- LÓGICA DA CENTRAL DE AJUDA ---
    const helpModal = document.getElementById('helpModal');
    if (helpModal) {
        // ... (código da Central de Ajuda continua o mesmo) ...
    }

    // --- LÓGICA DO PAINEL ---
    const abandonoTipoSelect = document.getElementById('abandono-tipo-select');
    if (abandonoTipoSelect) {
        // ... (código do seletor 'Presente Surpresa' continua o mesmo) ...
    }

    const configForm = document.getElementById('config-form');
    if (configForm) {
        // ... (código do formulário de salvar continua o mesmo) ...
    }

    const copiarBtn = document.getElementById('copiar-codigo-btn');
    if (copiarBtn) {
        // ... (código de copiar continua o mesmo) ...
    }
    
    // --- LÓGICA DA PÁGINA INICIAL ---

    // Abas do Modal de Login/Registro
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            tabButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            const tab = button.getAttribute('data-tab');
            tabContents.forEach(content => {
                if (content.id === tab + 'Tab') {
                    content.classList.add('active');
                } else {
                    content.classList.remove('active');
                }
            });
        });
    });

    // Lógica para o BOTÃO TEST DRIVE (Login Demo) - VERSÃO ROBUSTA
    const demoLoginBtn = document.getElementById('demoLoginBtn');
    if (demoLoginBtn) {
        demoLoginBtn.addEventListener('click', function() {
            // Simplesmente redireciona para a nossa nova rota de login demo
            window.location.href = '/demo-login';
        });
    }
});