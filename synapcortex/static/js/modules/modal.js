// static/js/components/auth-modal.js (v5.0 - SynapCortex Future-Ready)
// =================================================================================
// SYNAPCORTEX - WEB COMPONENT DE AUTENTICAÇÃO
// Arquitetura de Web Component com Shadow DOM para encapsulamento total,
// gerenciamento de estado, internacionalização e preparado para o futuro.
// =================================================================================

// Simulação de um módulo de internacionalização (i18n)
const translations = {
    'pt-BR': {
        'show_password': 'Mostrar senha',
        'hide_password': 'Ocultar senha',
        'error_required': 'Este campo é obrigatório.',
        'error_email': 'Por favor, insira um e-mail válido.',
        'error_password_short': (len) => `A senha precisa ter no mínimo ${len} caracteres.`,
        'error_cnpj_pattern': 'O CNPJ deve conter 14 números.',
        'login_failed': 'Credenciais inválidas. Verifique seu e-mail e senha.',
    },
    'en-US': {
        // ... Traduções para o inglês
    }
};

class AuthModal extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' }); // Ativa o Shadow DOM! 캡슐화
        
        // Cérebro do Componente: Gerenciamento de Estado Centralizado
        this.state = {
            isOpen: false,
            activeTab: 'login', // 'login' ou 'register'
            isLoading: false,
            lang: 'pt-BR', // Pode ser alterado dinamicamente
            errors: {}
        };
    }
    
    // Método de tradução para suportar globalização
    _t(key, ...args) {
        const message = translations[this.state.lang][key];
        return typeof message === 'function' ? message(...args) : message;
    }

    // --- CICLO DE VIDA DO WEB COMPONENT ---

    connectedCallback() {
        this._render();
        this._bindGlobalEvents();
    }

    // --- MÉTODOS PÚBLICOS (API DO COMPONENTE) ---

    open() {
        this.state.isOpen = true;
        this._render();
        document.body.classList.add('modal-open');
        // Foco inteligente no primeiro campo visível
        setTimeout(() => this.shadowRoot.querySelector('form:not([hidden]) input:not([type="hidden"])')?.focus(), 150);
    }

    close() {
        this.state.isOpen = false;
        this._render();
        document.body.classList.remove('modal-open');
    }

    // --- LÓGICA INTERNA ---

    _bindGlobalEvents() {
        // Ouve o evento para abrir o modal, disparado de qualquer lugar da aplicação
        document.addEventListener('open-auth-modal', () => this.open());
        // Fechar com a tecla 'Escape'
        document.addEventListener('keydown', (e) => {
            if (e.key === "Escape" && this.state.isOpen) this.close();
        });
    }

    _bindScopedEvents() {
        // Eventos internos, dentro do Shadow DOM
        const modal = this.shadowRoot.querySelector('.modal-container');
        if (!modal) return;

        modal.querySelector('.close-button').addEventListener('click', () => this.close());
        modal.addEventListener('click', (e) => { if (e.target === modal) this.close(); });

        this.shadowRoot.querySelectorAll('.tab-button').forEach(btn => 
            btn.addEventListener('click', (e) => this._handleTabSwitch(e))
        );
        
        this.shadowRoot.querySelectorAll('form').forEach(form => 
            form.addEventListener('submit', (e) => this._handleFormSubmit(e))
        );
        
        // ... outros eventos como toggle de senha, máscara de CNPJ ...
    }
    
    _handleTabSwitch(event) {
        this.state.activeTab = event.currentTarget.dataset.tab;
        this.state.errors = {}; // Limpa os erros ao trocar de aba
        this._render();
        setTimeout(() => this.shadowRoot.querySelector('form:not([hidden]) input:not([type="hidden"])')?.focus(), 50);
    }
    
    // Submissão de formulário ASSÍNCRONA e MODERNA
    async _handleFormSubmit(event) {
        event.preventDefault();
        const form = event.currentTarget;
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        // Validação com Zod (exemplo conceitual)
        // const schema = form.id === 'loginForm' ? loginSchema : registerSchema;
        // const validation = schema.safeParse(data);
        // if (!validation.success) { /* ... atualizar estado de erro ... */ return; }

        this.state.isLoading = true;
        this._render();

        try {
            // Lógica de chamada à API da SynapCortex
            const response = await fetch(form.action, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': data.csrfmiddlewaretoken },
                body: JSON.stringify(data),
            });
            
            const result = await response.json();

            if (!response.ok) {
                // Se a API retornar erros específicos dos campos
                if (result.errors) this.state.errors = result.errors;
                else this.state.errors = { general: this._t('login_failed') };
                
                // UX: Micro-interação de erro
                this.shadowRoot.querySelector('.modal-content').classList.add('shake');
                setTimeout(() => this.shadowRoot.querySelector('.modal-content').classList.remove('shake'), 500);

            } else {
                // Sucesso! Redirecionar ou atualizar a página
                window.location.href = result.redirect_url || '/dashboard';
            }

        } catch (error) {
            this.state.errors = { general: 'Ocorreu um erro de conexão. Tente novamente.' };
            console.error('SynapCortex Auth Error:', error);
        } finally {
            this.state.isLoading = false;
            this._render();
        }
    }

    _render() {
        // Template central do nosso componente. Re-renderiza baseado no estado.
        // Isso simplifica TODA a lógica de manipulação de DOM.
        this.shadowRoot.innerHTML = `
            <style>
                /* Estilos encapsulados do Modal - Inspirado no seu style.css */
                :host {
                    --sc-primary: #0A0A0A; /* Ex: Preto SynapCortex */
                    --sc-accent: #00F5D4; /* Ex: Ciano futurista */
                    --sc-text: #EAEAEA;
                    --sc-error: #FF5A5F;
                }
                .modal-overlay { /* ... estilos do overlay ... */ }
                .modal-content { /* ... estilos do conteúdo ... */ }
                .shake {
                    animation: shake 0.5s cubic-bezier(.36,.07,.19,.97) both;
                }
                @keyframes shake { /* ... keyframes da animação shake ... */ }
                /* ... TODOS OS OUTROS ESTILOS AQUI DENTRO ... */
            </style>
            
            <div class="modal-container" role="dialog" aria-modal="true" ${this.state.isOpen ? '' : 'hidden'}>
                <div class="modal-overlay"></div>
                <div class="modal-content">
                    <button class="close-button">&times;</button>
                    
                    <div class="brand-header">
                        <h2>SynapCortex</h2>
                        <p>O futuro da inteligência de negócios.</p>
                    </div>

                    <div class="tab-container">
                        <button data-tab="login" class="tab-button ${this.state.activeTab === 'login' ? 'active' : ''}">Entrar</button>
                        <button data-tab="register" class="tab-button ${this.state.activeTab === 'register' ? 'active' : ''}">Registrar</button>
                    </div>

                    <form id="loginForm" action="/accounts/login/" method="POST" ${this.state.activeTab === 'login' ? '' : 'hidden'}>
                        <button type="submit" ${this.state.isLoading ? 'disabled' : ''}>
                            ${this.state.isLoading ? '<div class="spinner"></div>' : 'Entrar'}
                        </button>
                    </form>
                    
                    <form id="registerForm" action="/accounts/register/" method="POST" ${this.state.activeTab === 'register' ? '' : 'hidden'}>
                        <button type="submit" ${this.state.isLoading ? 'disabled' : ''}>
                             ${this.state.isLoading ? '<div class="spinner"></div>' : 'Criar Conta'}
                        </button>
                    </form>
                    
                    <div class="divider">ou</div>

                    <div class="future-auth">
                         <button id="passkey-btn" class="passkey-button">Entrar sem Senha (Passkey)</button>
                        
                        <div class="social-logins">
                           <button class="social-btn google">Google</button>
                           <button class="social-btn linkedin">LinkedIn</button>
                        </div>
                    </div>

                </div>
            </div>
        `;
        this._bindScopedEvents(); // Re-conecta eventos internos após renderizar
    }
}

// Define o novo elemento personalizado para o navegador
customElements.define('auth-modal', AuthModal);

// Para usar na página:
// 1. Adicione <auth-modal></auth-modal> no seu HTML base.
// 2. Para abrir, dispare o evento:
//    document.dispatchEvent(new CustomEvent('open-auth-modal'));
//    Ex: <button onclick="document.dispatchEvent(new CustomEvent('open-auth-modal'))">Login</button>