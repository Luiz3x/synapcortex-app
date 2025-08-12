// =================================================================================
// SYNAPCORTEX - SCRIPT MESTRE (VERSÃO PENTE FINO)
// Versão 3.0 - Arquitetura unificada e final com todas as lógicas.
// =================================================================================

document.addEventListener('DOMContentLoaded', function() {
    
    // Tenta inicializar o agente espião. Se conseguir, para a execução aqui.
    if (synapseAgent.init()) {
        runSynapseAgent();
        return; 
    }
    
    // Se não for o espião, executa a lógica do nosso site/painel.
    runSynapCortexSiteLogic();
});

// =============================================================================
// PARTE 1: O AGENTE SYNAPSE (SÓ RODA NO SITE DO CLIENTE)
// =============================================================================
const synapseAgent = {
    apiKey: null,
    backendUrl: null,
    visitorId: null,
    init: function() {
        const scriptTag = document.getElementById('synapcortex-spy-script');
        if (!scriptTag) return false;
        
        const scriptUrl = new URL(scriptTag.src);
        const key = scriptUrl.searchParams.get('key');
        if (!key) return false;

        this.apiKey = key;
        this.backendUrl = scriptTag.dataset.backendUrl || 'https://synapcortex-app.onrender.com';
        
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
            apiKey: this.apiKey, visitorId: this.visitorId,
            eventName: eventName, eventData: eventData
        };
        fetch(`${this.backendUrl}/api/track`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload), keepalive: true
        }).catch(err => console.error("SynapCortex: Falha ao enviar relatório.", err));
    }
};

function runSynapseAgent() {
    let popupMostradoNestaSessao = false;
    function mostrarPopup(motivo, titulo, mensagem) {
        if (popupMostradoNestaSessao) return;
        popupMostradoNestaSessao = true;
        synapseAgent.trackEvent('popup_exibido', { gatilho: motivo });

        const popupContainer = document.createElement('div');
        popupContainer.style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; z-index: 9999;';
        const popupContent = document.createElement('div');
        popupContent.style.cssText = 'background-color: white; padding: 20px 30px; border-radius: 8px; text-align: center; max-width: 400px; color: #333;';
        popupContent.innerHTML = `<h2>${titulo}</h2><p>${mensagem}</p><button id="synapcortex-close-popup" style="margin-top: 15px; padding: 10px 20px; border: none; background-color: #333; color: white; border-radius: 5px; cursor: pointer;">Fechar</button>`;
        popupContainer.appendChild(popupContent);
        document.body.appendChild(popupContainer);

        popupContainer.addEventListener('click', function(e) {
            if (e.target === this || e.target.id === 'synapcortex-close-popup') {
                document.body.removeChild(popupContainer);
            }
        });
    }

    function inicializarMotorDeGatilhos(config) {
        if (config.ativar_abandono) {
            document.addEventListener('mouseleave', function(e) {
                if (e.clientY <= 0) {
                    mostrarPopup('abandono_de_site', config.popup_titulo || 'Não vá embora!', config.popup_mensagem || 'Temos uma oferta especial.');
                }
            });
        }
    }

    synapseAgent.trackEvent('pagina_visitada', { url: window.location.pathname, title: document.title });
    fetch(`${synapseAgent.backendUrl}/api/get-client-config?key=${synapseAgent.apiKey}`)
        .then(response => response.json())
        .then(config => {
            if (config && !config.error) { inicializarMotorDeGatilhos(config); }
        })
        .catch(error => { console.error("SynapCortex: Falha ao obter configs.", error); });
}

// =============================================================================
// PARTE 2: LÓGICA DO NOSSO SITE (PÁGINA INICIAL E DASHBOARD)
// =============================================================================
function runSynapCortexSiteLogic() {
    // Lógica para o Modal de Login/Registro
    const loginRegisterModal = document.getElementById('loginRegisterModal');
    if (loginRegisterModal) {
        const openModalBtn = document.getElementById('openLoginRegisterModal');
        const closeModalBtn = loginRegisterModal.querySelector('.close-button');
        const tabs = loginRegisterModal.querySelectorAll('.tab-button');
        const tabContents = loginRegisterModal.querySelectorAll('.tab-content');
        const loginForm = document.getElementById('loginForm');
        const registerForm = document.getElementById('registerForm');

        openModalBtn.addEventListener('click', () => { loginRegisterModal.style.display = 'flex'; });
        closeModalBtn.addEventListener('click', () => { loginRegisterModal.style.display = 'none'; });
        window.addEventListener('click', (event) => { if (event.target == loginRegisterModal) { loginRegisterModal.style.display = 'none'; } });

        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const target = tab.dataset.tab;
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                tabContents.forEach(c => c.classList.remove('active'));
                document.getElementById(target + 'Tab').classList.add('active');
            });
        });

        loginForm.addEventListener('submit', function(event) {
            event.preventDefault();
            fetch('/login', { method: 'POST', body: new URLSearchParams(new FormData(loginForm)) })
                .then(response => { if (response.ok && response.redirected) { window.location.href = response.url; } else { alert("E-mail ou senha inválidos."); } })
                .catch(error => console.error('Erro no login:', error));
        });

        registerForm.addEventListener('submit', function(event) {
            event.preventDefault();
            fetch('/registrar', { method: 'POST', body: new URLSearchParams(new FormData(registerForm)) })
                .then(response => { if (response.ok && response.redirected) { window.location.href = response.url; } else { alert("Erro ao registrar."); } })
                .catch(error => console.error('Erro no registro:', error));
        });
    }

    // Lógica para o botão "Test Drive"
    const demoLoginBtn = document.getElementById('demoLoginBtn');
    if (demoLoginBtn) {
        demoLoginBtn.addEventListener('click', function() {
            const demoData = new URLSearchParams({ email: 'demo@synapcortex.com', password: 'demo' });
            fetch('/login', { method: 'POST', body: demoData })
                .then(response => { if (response.ok && response.redirected) { window.location.href = response.url; } else { alert("Não foi possível acessar a demonstração."); } })
                .catch(error => console.error('Erro no Test Drive:', error));
        });
    }

    // Lógica para o formulário de salvar configurações no Dashboard
    const configForm = document.getElementById('config-form');
    if (configForm) {
        configForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const formData = new FormData(configForm);
            const saveButton = configForm.querySelector('button[type="submit"]');
            const originalButtonText = saveButton.textContent;

            saveButton.textContent = 'Salvando...';
            saveButton.disabled = true;

            fetch('/salvar-configuracoes', { method: 'POST', body: new URLSearchParams(formData) })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        saveButton.textContent = 'Salvo com Sucesso!';
                        saveButton.style.backgroundColor = 'var(--success-green)';
                    } else {
                        saveButton.textContent = 'Erro ao Salvar';
                        saveButton.style.backgroundColor = 'var(--error-red)';
                    }
                    setTimeout(() => {
                        saveButton.disabled = false;
                        if (data.status === 'success') {
                            window.location.reload();
                        } else {
                            saveButton.textContent = originalButtonText;
                            saveButton.style.backgroundColor = '';
                        }
                    }, 2000);
                })
                .catch(error => {
                    console.error('Erro ao salvar:', error);
                    saveButton.disabled = false;
                    saveButton.textContent = 'Erro de Comunicação';
                    setTimeout(() => { saveButton.textContent = originalButtonText; }, 2000);
                });
        });
    }
}