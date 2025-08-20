// static/js/main_logic.js (v10.0 - Ponto de Entrada Unificado)
// =================================================================================
// SYNAPCORTEX - INICIALIZADOR PRINCIPAL DE SCRIPTS
// Este arquivo orquestra a inicialização de todos os módulos JS da aplicação.
// =================================================================================

import { initNotifications } from './modules/notifications.js';
import { initLoginRegisterModal } from './modules/modal.js';
import { initDashboardLogic } from './modules/dashboard.js';

/**
 * Função principal que é executada após o carregamento completo do DOM.
 * Garante que todos os elementos HTML estejam disponíveis antes de manipularmos eles.
 */
function main() {
    initNotifications();
    initLoginRegisterModal();
    initDashboardLogic();
}

// Ponto de entrada da execução.
document.addEventListener('DOMContentLoaded', main);