// static/js/main_logic.js (v11.0 - Arquitetura Otimizada e Modular)
// =================================================================================
// SYNAPCORTEX - INICIALIZADOR PRINCIPAL DE SCRIPTS
// Este arquivo orquestra a inicialização de todos os módulos JS da aplicação
// de forma inteligente, carregando apenas o necessário para cada página.
// =================================================================================

/**
 * Função auxiliar para carregar e inicializar um módulo de forma segura e sob demanda.
 * Previne que um erro em um módulo quebre toda a aplicação.
 * @param {string} modulePath - O caminho para o módulo JS.
 * @param {string} initFunction - O nome da função de inicialização exportada pelo módulo.
 */
const safeInitialize = async (modulePath, initFunction) => {
    try {
        // Usa a importação dinâmica para carregar o módulo apenas quando esta função é chamada.
        const module = await import(modulePath);
        if (module && typeof module[initFunction] === 'function') {
            module[initFunction]();
        } else {
            console.warn(`Função ${initFunction} não encontrada no módulo ${modulePath}`);
        }
    } catch (error) {
        console.error(`Falha ao carregar ou inicializar o módulo: ${modulePath}`, error);
    }
};

/**
 * Ponto de entrada principal da aplicação, executado após o carregamento do DOM.
 */
document.addEventListener('DOMContentLoaded', () => {
    console.log("SynapCortex Initializing...");

    // --- MÓDULOS GLOBAIS ---
    // Módulos que precisam rodar em todas as páginas (ex: sistema de notificações).
    // safeInitialize('./modules/notifications.js', 'initNotifications');

    // --- MÓDULOS CONDICIONAIS ---
    // A mágica acontece aqui: verificamos a presença de um elemento-chave
    // para decidir qual(is) módulo(s) carregar.

    // Carrega a lógica do modal de autenticação e do formulário adaptativo
    // apenas se o modal existir na página (ou seja, na landing page).
    if (document.getElementById('loginRegisterModal')) {
        safeInitialize('./modules/auth_modal.js', 'initAuthModal');
        safeInitialize('./modules/auth_form.js', 'initAdaptiveAuthForm');
    }

    // Carrega a lógica interativa do painel do usuário
    // apenas se o container do dashboard estiver presente.
    if (document.querySelector('.dashboard-container')) {
        // safeInitialize('./modules/dashboard.js', 'initDashboardLogic');
    }

    // Carrega a lógica de pagamento do Stripe
    // apenas se o elemento do formulário de pagamento estiver na página.
    if (document.getElementById('payment-element')) {
        safeInitialize('./modules/checkout.js', 'initCheckoutForm');
    }
    
    console.log("SynapCortex Initialization Complete.");
});