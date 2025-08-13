// =================================================================================
// SYNAPCORTEX - SCRIPT ESPIÃO (v3.7 - BARRA DE CONTAGEM REGRESSIVA)
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
    // A lógica dos gatilhos normais (Abandono, Vendedor Especialista) vai aqui
}

// --- FUNÇÃO PARA A BARRA DE CAMPANHA ---
function mostrarBarraDeContagem(campaignConfig, endDate) {
    // Evita criar a barra se ela já existir
    if (document.getElementById('synapcortex-countdown-bar')) return;

    const bar = document.createElement('div');
    bar.id = 'synapcortex-countdown-bar';
    bar.style.cssText = `
        position: fixed; top: 0; left: 0; width: 100%;
        background: linear-gradient(90deg, #C732D8, #00bfff);
        color: white; text-align: center; padding: 10px;
        font-size: 16px; font-weight: bold; z-index: 99999;
        font-family: sans-serif; box-shadow: 0 2px 5px rgba(0,0,0,0.3);
        display: flex; align-items: center; justify-content: center;
    `;
    
    const textSpan = document.createElement('span');
    textSpan.textContent = campaignConfig.countdown_bar_text || '';

    const timerSpan = document.createElement('span');
    timerSpan.id = 'synapcortex-timer';
    timerSpan.style.marginLeft = '10px';
    timerSpan.style.minWidth = '100px'; // Garante espaço para o timer

    bar.appendChild(textSpan);
    bar.appendChild(timerSpan);
    document.body.prepend(bar);

    // Empurra o conteúdo da página para baixo para a barra não cobrir nada
    document.body.style.transform = `translateY(${bar.offsetHeight}px)`;


    const targetDate = new Date(endDate).getTime();

    const countdownInterval = setInterval(function() {
        const now = new Date().getTime();
        const distance = targetDate - now;

        if (distance < 0) {
            clearInterval(countdownInterval);
            bar.textContent = "OFERTA ENCERRADA!";
            setTimeout(() => {
                document.body.removeChild(bar);
                document.body.style.transform = 'translateY(0px)';
            }, 3000);
            return;
        }

        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);

        timerSpan.textContent = `${hours.toString().padStart(2, '0')}h ${minutes.toString().padStart(2, '0')}m ${seconds.toString().padStart(2, '0')}s`;
    }, 1000);
}


// Auto-execução quando o script é carregado
if (synapcortexAgent.init()) {
    synapcortexAgent.trackEvent('pagina_visitada', { url: window.location.pathname, title: document.title });
    
    fetch(`${synapcortexAgent.backendUrl}/api/get-client-config?key=${synapcortexAgent.apiKey}`)
        .then(response => response.json())
        .then(config => {
            if (config && !config.error) {
                if (config.is_campaign_active) {
                    console.log("MODO CAMPANHA ATIVO!", config.campaign_config);
                    mostrarBarraDeContagem(config.campaign_config, config.campaign_end_date);
                } else {
                    inicializarMotorDeGatilhos(config);
                }
            }
        })
        .catch(error => console.error("SynapCortex Spy: Falha ao obter configs.", error));
}