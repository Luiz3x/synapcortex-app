// static/js/modules/auth_modal.js (v3.0 - Versão Unificada e Definitiva)
// =================================================================================
// SYNAPCORTEX - MÓDULO COMPLETO PARA O MODAL DE AUTENTICAÇÃO
// Contém toda a lógica de UX, validação e interatividade.
// =================================================================================

/**
 * Mostra uma mensagem de erro para um campo específico.
 */
function showError(inputElement, message) {
    const inputGroup = inputElement.closest('.input-group, .input-group-checkbox');
    if (!inputGroup) return;
    
    const errorContainer = inputGroup.querySelector('.error-message');
    if (errorContainer) {
        errorContainer.textContent = message;
    }
    inputElement.setAttribute('aria-invalid', 'true');
    inputGroup.classList.add('error'); // Adiciona classe para estilização do erro (ex: borda vermelha)
}

/**
 * Limpa a mensagem de erro de um campo.
 */
function clearError(inputElement) {
    const inputGroup = inputElement.closest('.input-group, .input-group-checkbox');
    if (!inputGroup) return;

    const errorContainer = inputGroup.querySelector('.error-message');
    if (errorContainer) {
        errorContainer.textContent = '';
    }
    inputElement.setAttribute('aria-invalid', 'false');
    inputGroup.classList.remove('error');
}

/**
 * Aplica uma máscara de CNPJ (XX.XXX.XXX/XXXX-XX) enquanto o usuário digita.
 */
function applyCnpjMask(cnpjInput) {
    cnpjInput.addEventListener('input', (e) => {
        let value = e.target.value.replace(/\D/g, '').substring(0, 14);
        value = value.replace(/(\d{2})(\d)/, '$1.$2');
        value = value.replace(/(\d{3})(\d)/, '$1.$2');
        value = value.replace(/(\d{3})(\d)/, '$1/$2');
        value = value.replace(/(\d{4})(\d)/, '$1-$2');
        e.target.value = value;
    });
}

/**
 * Inicializa a lógica principal do modal de autenticação.
 */
export function initAuthModal() {
    const modal = document.getElementById('loginRegisterModal');
    // O botão que abre o modal agora tem um ID específico para clareza
    const openBtn = document.getElementById('openLoginRegisterModal'); 
    if (!modal || !openBtn) return;

    const closeBtn = modal.querySelector('.close-button');
    const tabButtons = modal.querySelectorAll('.tab-button');
    const forms = modal.querySelectorAll('form');
    const passwordToggles = modal.querySelectorAll('.password-toggle');
    const cnpjInput = modal.querySelector('#register-cnpj');

    // --- Funções de Controle do Modal ---
    const openModal = () => {
        modal.hidden = false;
        modal.setAttribute('aria-hidden', 'false');
        document.body.classList.add('modal-open');
        setTimeout(() => modal.querySelector('input:not([type="hidden"])').focus(), 100); // Foca no primeiro campo
    };

    const closeModal = () => {
        modal.hidden = true;
        modal.setAttribute('aria-hidden', 'true');
        document.body.classList.remove('modal-open');
    };

    // --- Event Handlers ---
    openBtn.addEventListener('click', openModal);
    if (closeBtn) closeBtn.addEventListener('click', closeModal);
    modal.addEventListener('click', (event) => { if (event.target === modal) closeModal(); });
    document.addEventListener('keydown', (event) => { if (event.key === "Escape" && !modal.hidden) closeModal(); });

    // --- Lógica das Abas (Login/Registro) ---
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabId = button.dataset.tab;
            tabButtons.forEach(btn => {
                btn.classList.remove('active');
                btn.setAttribute('aria-selected', 'false');
            });
            modal.querySelectorAll('.tab-content').forEach(content => content.hidden = true);
            
            button.classList.add('active');
            button.setAttribute('aria-selected', 'true');
            const activeTabContent = document.getElementById(tabId + 'Tab');
            if (activeTabContent) {
                activeTabContent.hidden = false;
                setTimeout(() => activeTabContent.querySelector('input:not([type="hidden"])').focus(), 100);
            }
        });
    });

    // --- Lógica de UX dos Formulários ---
    passwordToggles.forEach(toggle => {
        toggle.addEventListener('click', () => {
            const passwordInput = toggle.previousElementSibling;
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            toggle.setAttribute('aria-label', type === 'password' ? 'Mostrar senha' : 'Ocultar senha');
            toggle.classList.toggle('visible');
        });
    });

    if(cnpjInput) applyCnpjMask(cnpjInput);

    // --- Validação Inteligente ---
    forms.forEach(form => {
        form.addEventListener('submit', (event) => {
            form.querySelectorAll('input').forEach(clearError);
            
            if (!form.checkValidity()) {
                event.preventDefault();
                form.querySelectorAll('input:invalid, select:invalid').forEach(input => {
                    let message = input.validationMessage; // Usa a mensagem padrão do navegador
                    if (input.validity.valueMissing) message = 'Este campo é obrigatório.';
                    if (input.type === 'email' && input.validity.typeMismatch) message = 'Por favor, insira um e-mail válido.';
                    if (input.id === 'register-password' && input.validity.tooShort) message = 'A senha precisa ter no mínimo 8 caracteres.';
                    if (input.id === 'register-cnpj' && input.validity.patternMismatch) message = 'O CNPJ deve conter 14 números.';
                    if (input.id === 'terms') message = 'Você deve aceitar os termos de serviço.';
                    showError(input, message);
                });
            } else {
                const submitButton = form.querySelector('button[type="submit"]');
                submitButton.disabled = true;
                submitButton.querySelector('.spinner')?.classList.remove('hidden');
                submitButton.querySelector('.button-text')?.classList.add('hidden');
            }
        });
    });
}