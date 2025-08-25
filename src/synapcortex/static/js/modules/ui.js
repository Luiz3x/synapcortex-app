// static/js/modules/ui.js (v1.0)
// =================================================================================
// SYNAPCORTEX - MÓDULO DE COMPONENTES DE INTERFACE REUTILIZÁVEIS
// =================================================================================

/**
 * Controla um componente de modal, abstraindo a lógica de abrir, fechar e eventos.
 * @param {object} options
 * @param {string} options.modalSelector - O seletor CSS para o elemento do modal (ex: '#helpModal').
 * @param {string} options.openTriggersSelector - O seletor CSS para o(s) botão(ões) que abre(m) o modal.
 * @param {string} [options.closeTriggersSelector] - O seletor CSS opcional para o(s) botão(ões) que fecha(m) o modal.
 */
export function initializeModal({ modalSelector, openTriggersSelector, closeTriggersSelector }) {
    const modal = document.querySelector(modalSelector);
    const openTriggers = document.querySelectorAll(openTriggersSelector);
    if (!modal || !openTriggers.length) return;

    const openModal = () => {
        modal.hidden = false;
        modal.setAttribute('aria-hidden', 'false');
        document.body.classList.add('modal-open');
    };

    const closeModal = () => {
        modal.hidden = true;
        modal.setAttribute('aria-hidden', 'true');
        document.body.classList.remove('modal-open');
    };

    openTriggers.forEach(trigger => trigger.addEventListener('click', openModal));

    // O seletor de fechamento pode incluir o botão 'x' e botões 'cancelar'
    const closeTriggers = modal.querySelectorAll(`.close-button, ${closeTriggersSelector || ''}`);
    closeTriggers.forEach(trigger => {
        // Remove seletores vazios ou inválidos
        if (trigger) trigger.addEventListener('click', closeModal);
    });

    // Fechar ao clicar no fundo (overlay)
    modal.addEventListener('click', (event) => {
        if (event.target === modal) closeModal();
    });

    // Fechar ao pressionar a tecla 'Escape'
    document.addEventListener('keydown', (event) => {
        if (event.key === "Escape" && !modal.hidden) closeModal();
    });
}