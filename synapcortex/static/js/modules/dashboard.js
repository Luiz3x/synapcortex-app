// =================================================================================
// SYNAPCORTEX - LÓGICA INTERATIVA DO PAINEL DE CONTROLE (ARQUITETURA REFINADA)
// =================================================================================

import { showNotification } from './notifications.js';
import { initializeModal } from './ui.js';

/**
 * Orquestra toda a lógica interativa do painel de controle.
 */
export function initDashboardLogic() {
    setupSettingsForm();
    setupHelpModal();
    setupApiCodeCopy();
    setupCancelAccountModal();
}

/**
 * Lida com o envio assíncrono do formulário de configurações.
 */
function setupSettingsForm() {
    const form = document.getElementById('config-form');
    if (!form) return;

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const saveButton = form.querySelector('button[type="submit"]');
        if (!saveButton) return;

        const originalButtonText = saveButton.textContent;
        saveButton.textContent = 'Salvando...';
        saveButton.disabled = true;

        try {
            const formData = new FormData(form);
            const response = await fetch(form.action, {
                method: 'POST',
                body: new URLSearchParams(formData)
            });

            const data = await response.json();
            // APRIMORAMENTO: Checa se a resposta da rede foi bem sucedida.
            if (!response.ok) {
                throw new Error(data.message || 'Erro do servidor');
            }

            showNotification(data.message, data.status);

        } catch (error) {
            console.error('Erro de comunicação ao salvar configurações:', error);
            showNotification(error.message || 'Erro de comunicação. Tente novamente.', 'error');
        } finally {
            saveButton.textContent = originalButtonText;
            saveButton.disabled = false;
        }
    });
}

/**
 * APRIMORAMENTO: Configura o modal de ajuda usando event delegation e o módulo de UI.
 */
function setupHelpModal() {
    const helpGrid = document.querySelector('.help-center-grid');
    const modal = document.querySelector('#helpModal');
    if (!helpGrid || !modal) return;

    const titleEl = document.getElementById('helpModalTitle');
    const contentEl = document.getElementById('helpModalContent');

    const helpData = { /* (Seus dados de ajuda aqui, sem alteração) */ };

    // APRIMORAMENTO: Um único listener no container pai. Mais eficiente.
    helpGrid.addEventListener('click', (event) => {
        const platformButton = event.target.closest('.platform-button');
        if (!platformButton) return;

        const platform = platformButton.dataset.platform;
        const data = helpData[platform];
        if (data) {
            titleEl.textContent = data.title;
            contentEl.innerHTML = data.content;
            // A abertura do modal é agora controlada pela função genérica.
        }
    });

    // A lógica de abrir/fechar agora é centralizada.
    initializeModal({
        modalSelector: '#helpModal',
        openTriggersSelector: '.platform-button',
    });
}

/**
 * Configura a funcionalidade de copiar o código de instalação.
 */
function setupApiCodeCopy() {
    const copyBtn = document.getElementById('copiar-codigo-btn');
    if (!copyBtn) return;

    copyBtn.addEventListener('click', async () => {
        const codeTextarea = document.getElementById('codigo-instalacao');
        try {
            await navigator.clipboard.writeText(codeTextarea.value);
            const originalText = copyBtn.textContent;
            copyBtn.textContent = 'Copiado!';
            showNotification('Código copiado com sucesso!', 'success');
            setTimeout(() => { copyBtn.textContent = originalText; }, 2000);
        } catch (err) {
            showNotification('Falha ao copiar o código.', 'error');
        }
    });
}

/**
 * APRIMORAMENTO: Configura o modal de cancelamento usando o módulo de UI.
 */
function setupCancelAccountModal() {
    const confirmBtn = document.getElementById('confirmar-cancelamento-btn');
    if (!confirmBtn) return;
    
    // A lógica de abrir/fechar o modal é delegada para nossa ferramenta.
    initializeModal({
        modalSelector: '#cancelModal',
        openTriggersSelector: '#cancelar-conta-btn',
        closeTriggersSelector: '[data-close-modal="cancelModal"]',
    });
    
    confirmBtn.addEventListener('click', async () => {
        confirmBtn.textContent = 'Encerrando...';
        confirmBtn.disabled = true;
        // APRIMORAMENTO: O endpoint agora é lido de um atributo de dados, desacoplando o JS do HTML.
        const endpoint = confirmBtn.dataset.endpoint;

        try {
            const response = await fetch(endpoint, { method: 'POST' });
            const data = await response.json();

            if (!response.ok) throw new Error(data.message || 'Ocorreu um erro');

            // O redirecionamento só acontece em caso de sucesso absoluto.
            window.location.href = data.redirect_url;
        } catch (error) {
            showNotification(error.message, 'error');
            confirmBtn.textContent = 'Sim, encerrar';
            confirmBtn.disabled = false;
        }
    });
}