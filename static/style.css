// spy.js - Versão 5.2 (Com Lógica de Login de Demonstração)

document.addEventListener('DOMContentLoaded', function() {

    // (TODOS OS MÓDULOS ANTERIORES - FERRAMENTAS, POP-UP, GATILHOS - CONTINUAM OS MESMOS)
    // ...

    // =================================================================================
    // MÓDULO 4: LÓGICA DA PÁGINA (GRÁFICO, MODAL, FORMULÁRIOS)
    // =================================================================================

    function inicializarLogicaDaPagina() {
        // --- GRÁFICO DE DEMONSTRAÇÃO (continua o mesmo) ---
        // ...

        // --- MODAL DE LOGIN/CADASTRO (continua o mesmo) ---
        const modal = document.getElementById('loginRegisterModal');
        const openModalBtn = document.getElementById('openLoginRegisterModal');
        // ... (resto da lógica do modal)

        // --- FORMULÁRIOS COM FETCH (continua o mesmo) ---
        // ...

        // >>> INÍCIO DA NOVA LÓGICA DO BOTÃO MÁGICO <<<
        const demoLoginBtn = document.getElementById('demoLoginBtn');
        if (demoLoginBtn) {
            demoLoginBtn.addEventListener('click', function() {
                // Pega os campos do formulário de login que já existem
                const emailField = document.getElementById('modal-email-login');
                const passwordField = document.getElementById('modal-password-login');
                const loginForm = document.getElementById('loginForm');

                if (emailField && passwordField && loginForm) {
                    // Preenche com os dados do nosso "Cliente Fantasma"
                    emailField.value = 'demo@synapcortex.com';
                    passwordField.value = 'demo'; // A senha real não importa, desde que o backend a reconheça
                    
                    // Dispara o envio do formulário
                    loginForm.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
                }
            });
        }
        // >>> FIM DA NOVA LÓGICA <<<
    }

    // (MÓDULO CENTRAL E INICIALIZAÇÃO GERAL CONTINUAM OS MESMOS)
    // ...
});