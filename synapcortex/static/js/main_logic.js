// static/js/main_logic.js (v13.0 - Intelligent Core Orchestrator)
// =================================================================================
// SYNAPCORTEX - CORE ORCHESTRATOR
// Evoluído para suportar estratégias de carregamento inteligentes (eager, visible, interaction)
// e otimizações preditivas para uma performance percebida instantânea.
// =================================================================================

/**
 * Módulo de Diagnósticos da SynapCortex.
 * Em um cenário real, isso se integraria a um serviço como Sentry.
 */
const Diagnostics = {
    reportError(error, context) {
        console.error(`[SynapCortex Diagnostics]`, context, error);
        // Em produção: Sentry.captureException(error, { extra: context });
    }
};

/**
 * Pre-carrega um módulo para acelerar futuras interações.
 * @param {string} path - O caminho para o módulo a ser pre-carregado.
 */
function preloadModule(path) {
    const link = document.createElement('link');
    link.rel = 'modulepreload';
    link.href = path;
    document.head.appendChild(link);
}


/**
 * Mapa de Módulos da Aplicação.
 * Cada módulo agora tem uma "estratégia" de carregamento.
 * - eager: Carrega imediatamente se o seletor for encontrado (comportamento antigo).
 * - visible: Carrega apenas quando o elemento entra na tela (usando IntersectionObserver).
 * - interaction: Carrega ao primeiro sinal de interação do usuário (clique, foco, hover).
 */
const appModules = [
    {
        // O Web Component do Modal: a melhor estratégia é 'interaction'.
        // Não precisamos do código dele até que o usuário demonstre intenção de usá-lo.
        name: 'AuthModal',
        selector: '[data-action="open-auth-modal"]',
        strategy: 'interaction',
        path: './components/auth-modal.js',
        async init(triggerElement) {
            // Apenas importar já registra o Web Component.
            await import(this.path); 
            // Uma vez carregado, disparamos o evento imediatamente para abrir.
            document.dispatchEvent(new CustomEvent('open-auth-modal'));
        }
    },
    {
        // O Dashboard: pode conter gráficos pesados. Carregar apenas quando for visível.
        name: 'Dashboard',
        selector: '.dashboard-container',
        strategy: 'visible',
        path: './modules/dashboard.js',
        async init(container) {
            const { initDashboardLogic } = await import(this.path);
            initDashboardLogic(container);
        }
    },
    {
        // O Checkout do Stripe: é crítico e deve carregar assim que a página estiver pronta.
        name: 'StripeCheckout',
        selector: '#payment-element',
        strategy: 'eager',
        path: './modules/checkout.js',
        async init(element) {
            const { initCheckoutForm } = await import(this.path);
            initCheckoutForm(element);
        }
    }
    // Adicionar futuros módulos aqui...
];

/**
 * O Orquestrador Inteligente da SynapCortex.
 * Inicializa os módulos da aplicação com base em suas estratégias de carregamento.
 */
function orchestrateApp() {
    console.log("SynapCortex Intelligent Orchestrator Initializing...");

    const visibleObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const module = appModules.find(m => m.selector === `#${entry.target.id}`);
                if(module) {
                    module.init(entry.target).catch(e => Diagnostics.reportError(e, { module: module.name }));
                    observer.unobserve(entry.target); // Carrega apenas uma vez
                }
            }
        });
    }, { rootMargin: '200px' }); // Otimização: começa a carregar 200px ANTES de ficar visível

    appModules.forEach(module => {
        const elements = document.querySelectorAll(module.selector);
        if (elements.length === 0) return;

        elements.forEach(element => {
            switch (module.strategy) {
                case 'eager':
                    module.init(element).catch(e => Diagnostics.reportError(e, { module: module.name }));
                    break;
                
                case 'visible':
                    // Para o observer funcionar, o elemento precisa de um ID único
                    if (!element.id) element.id = `sc-observed-${Math.random().toString(36).substr(2, 9)}`;
                    visibleObserver.observe(element);
                    break;
                    
                case 'interaction':
                    const runInit = () => module.init(element).catch(e => Diagnostics.reportError(e, { module: module.name }));
                    
                    // Otimização Preditiva: pre-carrega no hover!
                    element.addEventListener('mouseenter', () => preloadModule(module.path), { once: true });
                    
                    element.addEventListener('click', runInit, { once: true });
                    element.addEventListener('focus', runInit, { once: true });
                    break;
            }
        });
    });

    console.log("SynapCortex Orchestration Complete. Awaiting user interaction...");
}

// Inicia a orquestração.
document.addEventListener('DOMContentLoaded', orchestrateApp);