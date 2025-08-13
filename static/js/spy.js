// =================================================================================
// SYNAPCORTEX - SCRIPT ESPIÃO (v3.6 - VENDEDOR ESPECIALISTA)
// =================================================================================

const synapseAgent = {
    apiKey: null, backendUrl: null, visitorId: null,
    init: function() {
        const scriptTag = document.getElementById('synapcortex-spy-script');
        if (!scriptTag) return false;
        try {
            const key = new URL(scriptTag.src).searchParams.get('key');
            if (!key) return false;
            this.apiKey = key;
        } catch(e) { return false; }
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
        const payload = { apiKey: this.apiKey, visitorId: this.visitorId, eventName, eventData };
        try {
            navigator.sendBeacon(`${this.backendUrl}/api/track`, JSON.stringify(payload));
        } catch (e) {
            fetch(`${this.backendUrl}/api/track`, { method: 'POST', body: JSON.stringify(payload), headers: { 'Content-Type': 'application/json' }, keepalive: true }).catch(console.error);
        }
    }
};

function inicializarMotorDeGatilhos(config) {
    let popupMostradoNestaSessao = false;
    let paginasVisitadasNaSessao = JSON.parse(sessionStorage.getItem('synapcortex_session_pages')) || {};

    const urlAtual = window.location.pathname;
    paginasVisitadasNaSessao[urlAtual] = (paginasVisitadasNaSessao[urlAtual] || 0) + 1;
    sessionStorage.setItem('synapcortex_session_pages', JSON.stringify(paginasVisitadasNaSessao));

    function mostrarPopup(motivo, titulo, mensagem) {
        if (popupMostradoNestaSessao) return;
        popupMostradoNestaSessao = true;
        synapseAgent.trackEvent('popup_exibido', { gatilho: motivo });

        const popupContainer = document.createElement('div');
        popupContainer.style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; z-index: 9999; font-family: sans-serif;';
        const popupContent = document.createElement('div');
        popupContent.style.cssText = 'background-color: white; padding: 25px; border-radius: 8px; text-align: center; max-width: 90%; width: 450px; color: #333;';
        popupContent.innerHTML = `<h2 style="margin-bottom: 10px;">${titulo || ''}</h2><p>${mensagem || ''}</p><button id="synapcortex-close-popup" style="margin-top: 20px; padding: 10px 20px; border: none; background-color: #333; color: white; border-radius: 5px; cursor: pointer;">Fechar</button>`;
        
        popupContainer.appendChild(popupContent);
        document.body.appendChild(popupContainer);

        popupContainer.addEventListener('click', function(e) {
            if (e.target === this || e.target.id === 'synapcortex-close-popup') {
                document.body.removeChild(popupContainer);
            }
        });
    }

    // --- GATILHO 1: ABANDONO DE CARRINHO ---
    if (config.ativar_abandono) {
        document.addEventListener('mouseleave', function(e) {
            if (e.clientY <= 0) {
                mostrarPopup('abandono_de_site', config.popup_titulo, config.popup_mensagem);
            }
        });
    }

    // --- GATILHO 2: VENDEDOR ESPECIALISTA ---
    if (config.ativar_quarto_bem_vindo && paginasVisitadasNaSessao[urlAtual] >= 3) {
        setTimeout(() => {
            mostrarPopup('vendedor_especialista', 'Um Interesse Especial?', config.msg_bem_vindo);
        }, 2000);
    }
}

// Auto-execução quando o script é carregado
if (synapseAgent.init()) {
    synapseAgent.trackEvent('pagina_visitada', { url: window.location.pathname, title: document.title });
    
    fetch(`${synapseAgent.backendUrl}/api/get-client-config?key=${synapseAgent.apiKey}`)
        .then(response => response.json())
        .then(config => {
            if (config && !config.error) {
                inicializarMotorDeGatilhos(config);
            }
        })
        .catch(error => console.error("SynapCortex Spy: Falha ao obter configs.", error));
}