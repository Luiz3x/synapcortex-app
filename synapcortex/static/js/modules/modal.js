// static/js/modules/modal.js (v1.0 - Lógica do Modal de Autenticação)
// =================================================================================
// SYNAPCORTEX - MÓDULO PARA O MODAL DE LOGIN/REGISTRO
// =================================================================================

export function initLoginRegisterModal() {
    const openBtn = document.getElementById('openLoginRegisterModal');
    const modal = document.getElementById('loginRegisterModal');
    
    // Se não estivermos na página inicial, não faz nada.
    if (!openBtn || !modal) return;

    const closeBtn = modal.querySelector('.close-button');
    const tabButtons = modal.querySelectorAll('.tab-button');

    const openModal = () => {
        modal.style.display = 'flex';
        document.body.classList.add('modal-open');
    };

    const closeModal = () => {
        modal.style.display = 'none';
        document.body.classList.remove('modal-open');
    };

    // Evento para abrir o modal
    openBtn.addEventListener('click', openModal);

    // Evento para fechar no botão 'x'
    if (closeBtn) closeBtn.addEventListener('click', closeModal);

    // Evento para fechar clicando fora (no overlay)
    modal.addEventListener('click', (event) => {
        if (event.target === modal) closeModal();
    });

    // Lógica para alternar entre as abas de Login e Registro
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabId = button.dataset.tab + 'Tab';
            modal.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
            modal.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            button.classList.add('active');
            
            const activeTabContent = document.getElementById(tabId);
            if(activeTabContent) {
                activeTabContent.classList.add('active');
            }
        });
    });
}