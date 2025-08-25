// synapcortex/static/js/dashboard.js (v2.0 - Arquitetura Profissional)
// =================================================================================
// SYNAPCORTEX - LÓGICA INTERATIVA DO PAINEL DE CONTROLE
// =================================================================================

import { showNotification } from './notifications.js';
import { initializeModal } from './ui.js';

// --- FUNÇÕES AUXILIARES ---

/**
 * Alterna o estado de um botão (ativado/desativado) e seu texto.
 * @param {HTMLButtonElement} button - O elemento do botão.
 * @param {boolean} isLoading - Se deve exibir o estado de "carregando".
 * @param {string} originalText - O texto original do botão.
 */
const toggleButtonState = (button, isLoading, originalText = 'Salvar') => {
    button.disabled = isLoading;
    button.textContent = isLoading ? 'Salvando...' : originalText;
};

/**
 * Realiza uma requisição fetch padronizada com tratamento de erro.
 * @param {string} url - O endpoint da API.
 * @param {object} options - As opções da requisição (método, corpo, etc.).
 * @returns {Promise<object>} - Os dados da resposta em JSON.
 */
async function apiRequest(url, options = {}) {
    try {
        // APRIMORAMENTO: Inclui o token CSRF para segurança, se disponível.
        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
        const headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            ...options.headers,
            ...(csrfToken && { 'X-CSRFToken': csrfToken }),
        };

        const response = await fetch(url, { ...options, headers });
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || `Erro ${response.status}`);
        }
        return data;

    } catch (error) {
        console.error(`Erro na API [${options.method || 'GET'} ${url}]:`, error);
        showNotification(error.message || 'Erro de comunicação. Tente novamente.', 'error');
        throw error; // Re-lança o erro para que a função que chamou possa tratá-lo.
    }
}


// --- LÓGICA PRINCIPAL ---

/**
 * Lida com o envio do formulário de configurações.
 * @param {Event} event
 */
async function handleSettingsFormSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const saveButton = form.querySelector('button[type="submit"]');
    if (!saveButton) return;
    
    const originalButtonText = saveButton.textContent;
    toggleButtonState(saveButton, true);

    try {
        const formData = new FormData(form);
        const data = await apiRequest(form.action, {
            method: 'POST',
            body: new URLSearchParams(formData)
        });
        showNotification(data.message, data.status);
    } catch (error) {
        // O erro já é notificado pelo apiRequest
    } finally {
        toggleButtonState(saveButton, false, originalButtonText);
    }
}

/**
 * Lida com a cópia do código de instalação para a área de transferência.
 * @param {HTMLElement} copyBtn - O botão de cópia.
 */
async function handleApiCodeCopy(copyBtn) {
    const codeTextarea = document.getElementById('codigo-instalacao');
    if (!codeTextarea) return;

    try {
        await navigator.clipboard.writeText(codeTextarea.value);
        const originalText = copyBtn.textContent;
        copyBtn.textContent = 'Copiado!';
        showNotification('Código copiado com sucesso!', 'success');
        setTimeout(() => { copyBtn.textContent = originalText; }, 2000);
    } catch (err) {
        showNotification('Falha ao copiar o código.', 'error');
    }
}

/**
 * Lida com a confirmação de cancelamento da conta.
 * @param {HTMLButtonElement} confirmBtn - O botão de confirmação.
 */
async function handleCancelAccount(confirmBtn) {
    const originalText = confirmBtn.textContent;
    confirmBtn.textContent = 'Encerrando...';
    confirmBtn.disabled = true;

    try {
        const endpoint = confirmBtn.dataset.endpoint;
        const data = await apiRequest(endpoint, { method: 'POST' });
        // O redirecionamento só acontece em caso de sucesso absoluto.
        if (data.redirect_url) {
            window.location.href = data.redirect_url;
        }
    } catch (error) {
        confirmBtn.textContent = originalText;
        confirmBtn.disabled = false;
    }
}

/**
 * Orquestra toda a lógica interativa do painel, executando quando a página carrega.
 */
document.addEventListener('DOMContentLoaded', () => {
    // Inicialização dos Modais (usando a ferramenta de UI genérica)
    initializeModal({ modalSelector: '#helpModal', openTriggersSelector: '.platform-button' });
    initializeModal({
        modalSelector: '#cancelModal',
        openTriggersSelector: '#cancelar-conta-btn',
        closeTriggersSelector: '[data-close-modal="cancelModal"]',
    });

    // APRIMORAMENTO: Central de Eventos com Event Delegation
    document.body.addEventListener('click', (event) => {
        const target = event.target;
        
        if (target.matches('#copiar-codigo-btn')) {
            handleApiCodeCopy(target);
        }
        
        if (target.matches('#confirmar-cancelamento-btn')) {
            handleCancelAccount(target);
        }
    });

    // Listener específico para o submit do formulário
    const settingsForm = document.getElementById('config-form');
    if (settingsForm) {
        settingsForm.addEventListener('submit', handleSettingsFormSubmit);
    }
});