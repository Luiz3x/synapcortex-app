// =================================================================================
// SYNAPCORTEX - SCRIPT MESTRE (AGENTE SYNAPSE + LÓGICA DO SITE)
// Versão 2.5 - Adicionada a lógica de submissão para os formulários de login e registro.
// =================================================================================

document.addEventListener('DOMContentLoaded', function() {
    
    // -----------------------------------------------------------------------------
    // PARTE 1: LÓGICA DO NOSSO SITE (PÁGINA PRINCIPAL E DASHBOARD)
    // -----------------------------------------------------------------------------
    
    const loginRegisterModal = document.getElementById('loginRegisterModal');
    
    if (loginRegisterModal) {
        const openModalBtn = document.getElementById('openLoginRegisterModal');
        const closeModalBtn = loginRegisterModal.querySelector('.close-button');
        const tabs = loginRegisterModal.querySelectorAll('.tab-button');
        const tabContents = loginRegisterModal.querySelectorAll('.tab-content');
        const loginForm = document.getElementById('loginForm');
        const registerForm = document.getElementById('registerForm');

        if(openModalBtn) {
            openModalBtn.addEventListener('click', () => {
                loginRegisterModal.style.display = 'flex';
            });
        }

        closeModalBtn.addEventListener('click', () => {
            loginRegisterModal.style.display = 'none';
        });

        window.addEventListener('click', (event) => {
            if (event.target == loginRegisterModal) {
                loginRegisterModal.style.display = 'none';
            }
        });

        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const target = tab.dataset.tab;
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                tabContents.forEach(c => c.classList.remove('active'));
                document.getElementById(target + 'Tab').classList.add('active');
            });
        });

        // [NOVO] Lógica para o formulário de LOGIN
        if (loginForm) {
            loginForm.addEventListener('submit', function(event) {
                event.preventDefault(); // Impede o recarregamento da página (a "piscada")
                const formData = new FormData(loginForm);
                fetch('/login', {
                    method: 'POST',
                    body: new URLSearchParams(formData)
                }).then(response => {
                    if (response.ok && response.redirected) {
                        window.location.href = response.url; // Redireciona para o dashboard
                    } else {
                        // Se houver erro, o backend pode retornar uma mensagem
                        // (requer ajuste no backend para retornar JSON em caso de falha)
                        alert("E-mail ou senha inválidos.");
                        // Futuramente, podemos exibir a mensagem de erro em um campo específico
                    }
                }).catch(error => console.error('Erro no login:', error));
            });
        }

        // [NOVO] Lógica para o formulário de REGISTRO
        if (registerForm) {
            registerForm.addEventListener('submit', function(event) {
                event.preventDefault(); // Impede o recarregamento da página
                const formData = new FormData(registerForm);
                fetch('/registrar', {
                    method: 'POST',
                    body: new URLSearchParams(formData)
                }).then(response => {
                    if (response.ok && response.redirected) {
                        window.location.href = response.url; // Redireciona para o dashboard
                    } else {
                        // Tratar erro de registro (ex: email já existe)
                         alert("Erro ao registrar. Verifique os dados ou o e-mail pode já estar em uso.");
                    }
                }).catch(error => console.error('Erro no registro:', error));
            });
        }
    }


    // -----------------------------------------------------------------------------
    // PARTE 2: O AGENTE SYNAPSE E O ESPIÃO (PARA SITES DE CLIENTES)
    // -----------------------------------------------------------------------------
    const synapseAgent = {
        apiKey: null,
        backendUrl: null,
        visitorId: null,

        init: function() {
            const scriptTag = document.getElementById('synapcortex-spy-script');
            if (!scriptTag) return false;
            this.backendUrl = scriptTag.dataset.backendUrl || window.location.origin;
            const scriptUrl = new URL(scriptTag.src);
            this.apiKey = scriptUrl.searchParams.get('key');
            if (!this.apiKey) return false;

            let storedVisitorId = localStorage.getItem('synapcortex_visitor_id');
            if (!storedVisitorId) {
                storedVisitorId = Date.now() + '-' + Math.random().toString(36).substr(2, 9);
                localStorage.setItem('synapcortex_visitor_id', storedVisitorId);
            }
            this.visitorId = storedVisitorId;
            return true;
        },

        trackEvent: function(eventName, eventData = {}) {
            if (!this.apiKey) return;
            const payload = {
                apiKey: this.apiKey,
                visitorId: this.visitorId,
                eventName: eventName,
                eventData: eventData
            };
            fetch(`${this.backendUrl}/api/track`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
                keepalive: true
            }).catch(err => console.error("SynapCortex: Falha ao enviar relatório.", err));
        }
    };

    let popupMostradoNestaSessao = false;
    function mostrarPopup(motivo, titulo, mensagem) {
        if (popupMostradoNestaSessao) return;
        popupMostradoNestaSessao = true;
        synapseAgent.trackEvent('popup_exibido', { gatilho: motivo });
        // Lógica para criar e mostrar o HTML do pop-up
    }

    function inicializarMotorDeGatilhos(config) {
        // Lógica dos gatilhos de abandono, bem-vindo, etc.
    }

    // --- BLOCO DE EXECUÇÃO PRINCIPAL DO AGENTE ---
    if (synapseAgent.init()) {
        synapseAgent.trackEvent('pagina_visitada', { url: window.location.pathname, title: document.title });

        fetch(`${synapseAgent.backendUrl}/api/get-client-config?key=${synapseAgent.apiKey}`)
            .then(response => response.json())
            .then(config => {
                if (config && !config.error) {
                    inicializarMotorDeGatilhos(config);
                }
            })
            .catch(error => { console.error("SynapCortex: Falha ao obter configs.", error); });
    }
});