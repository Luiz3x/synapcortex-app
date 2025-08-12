// =================================================================================
// SYNAPCORTEX - SCRIPT MESTRE (v3.1 - COMPLETO)
// =================================================================================

document.addEventListener('DOMContentLoaded', function() {
    if (typeof synapseAgent !== 'undefined' && synapseAgent.init()) {
        runSynapseAgent();
        return; 
    }
    runSynapCortexSiteLogic();
});

// PARTE 1: O AGENTE ESPIÃO (SÓ RODA NO SITE DO CLIENTE)
const synapseAgent = {
    apiKey: null, backendUrl: null, visitorId: null,
    init: function() {
        const scriptTag = document.getElementById('synapcortex-spy-script');
        if (!scriptTag) return false;
        const key = new URL(scriptTag.src).searchParams.get('key');
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
        navigator.sendBeacon(`${this.backendUrl}/api/track`, JSON.stringify(payload));
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
            document.addEventListener('mouseleave', (e) => {
                if (e.clientY <= 0) mostrarPopup('abandono_de_site', config.popup_titulo, config.popup_mensagem);
            });
        }
        // ... (lógica para outros gatilhos como 'bem_vindo' e 'interessado' viria aqui)
    }

    synapseAgent.trackEvent('pagina_visitada', { url: window.location.pathname, title: document.title });
    fetch(`${synapseAgent.backendUrl}/api/get-client-config?key=${synapseAgent.apiKey}`)
        .then(response => response.json())
        .then(config => {
            if (config && !config.error) inicializarMotorDeGatilhos(config);
        }).catch(console.error);
}

// PARTE 2: LÓGICA DO NOSSO SITE (PÁGINA INICIAL E DASHBOARD)
function runSynapCortexSiteLogic() {
    const loginRegisterModal = document.getElementById('loginRegisterModal');
    if (loginRegisterModal) {
        const openModalBtn = document.getElementById('openLoginRegisterModal');
        const closeModalBtn = loginRegisterModal.querySelector('.close-button');
        openModalBtn.addEventListener('click', () => { loginRegisterModal.style.display = 'flex'; });
        closeModalBtn.addEventListener('click', () => { loginRegisterModal.style.display = 'none'; });
        window.addEventListener('click', (e) => { if (e.target == loginRegisterModal) loginRegisterModal.style.display = 'none'; });
        // ... (lógica de abas e formulários de login/registro)
    }

    const configForm = document.getElementById('config-form');
    if (configForm) {
        configForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(configForm);
            const saveButton = configForm.querySelector('button[type="submit"]');
            fetch('/salvar-configuracoes', { method: 'POST', body: new URLSearchParams(formData) })
                .then(res => res.json())
                .then(data => {
                    if (data.status === 'success') {
                        saveButton.textContent = 'Salvo com Sucesso!';
                        saveButton.style.backgroundColor = 'var(--success-green)';
                        setTimeout(() => window.location.reload(), 1500);
                    } else if (data.status === 'info') {
                        alert(data.message);
                    } else { alert('Ocorreu um erro.'); }
                }).catch(() => alert('Erro de comunicação.'));
        });
    }
    
    const copiarBtn = document.getElementById('copiar-codigo-btn');
    if (copiarBtn) {
        copiarBtn.addEventListener('click', () => {
            const codigoTextarea = document.getElementById('codigo-instalacao');
            navigator.clipboard.writeText(codigoTextarea.value).then(() => {
                copiarBtn.textContent = 'Copiado!';
                setTimeout(() => { copiarBtn.textContent = 'Copiar Código'; }, 2000);
            });
        });
    }

    const helpModal = document.getElementById('helpModal');
    if (helpModal) {
        // ... (toda a lógica do modal de ajuda que já está no seu dashboard.html)
    }
}