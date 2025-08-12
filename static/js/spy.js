// =================================================================================
// SYNAPCORTEX - SCRIPT MESTRE (AGENTE SYNAPSE + LÓGICA DO SITE)
// Versão 2.7 - Versão unificada e completa. Contém todas as lógicas.
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

        if (loginForm) {
            loginForm.addEventListener('submit', function(event) {
                event.preventDefault();
                const formData = new FormData(loginForm);
                fetch('/login', {
                    method: 'POST',
                    body: new URLSearchParams(formData)
                }).then(response => {
                    if (response.ok && response.redirected) {
                        window.location.href = response.url;
                    } else {
                        alert("E-mail ou senha inválidos.");
                    }
                }).catch(error => console.error('Erro no login:', error));
            });
        }

        if (registerForm) {
            registerForm.addEventListener('submit', function(event) {
                event.preventDefault();
                const formData = new FormData(registerForm);
                fetch('/registrar', {
                    method: 'POST',
                    body: new URLSearchParams(formData)
                }).then(response => {
                    if (response.ok && response.redirected) {
                        window.location.href = response.url;
                    } else {
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

        const popupContainer = document.createElement('div');
        popupContainer.style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; z-index: 9999;';
        
        const popupContent = document.createElement('div');
        popupContent.style.cssText = 'background-color: white; padding: 20px 30px; border-radius: 8px; text-align: center; max-width: 400px; box-shadow: 0 5px 15px rgba(0,0,0,0.3);';
        
        const popupTitle = document.createElement('h2');
        popupTitle.textContent = titulo;
        
        const popupMessage = document.createElement('p');
        popupMessage.textContent = mensagem;
        
        const closeButton = document.createElement('button');
        closeButton.textContent = 'Fechar';
        closeButton.style.cssText = 'margin-top: 15px; padding: 10px 20px; border: none; background-color: #333; color: white; border-radius: 5px; cursor: pointer;';
        
        popupContent.appendChild(popupTitle);
        popupContent.appendChild(popupMessage);
        popupContent.appendChild(closeButton);
        popupContainer.appendChild(popupContent);
        
        document.body.appendChild(popupContainer);

        closeButton.onclick = () => { document.body.removeChild(popupContainer); };
        popupContainer.onclick = (e) => { if(e.target === popupContainer){ document.body.removeChild(popupContainer); } };
    }

    function inicializarMotorDeGatilhos(config) {
        if (config.ativar_abandono) {
            document.addEventListener('mouseleave', function(e) {
                if (e.clientY <= 0) {
                    mostrarPopup('abandono_de_site', config.popup_titulo || 'Não vá embora!', config.popup_mensagem || 'Temos uma oferta especial para você.');
                }
            });
        }
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