// =================================================================================
// SYNAPCORTEX - SCRIPT ESPIÃO (v3.7 - BARRA DE CONTAGEM REGRESSIVA)
// =================================================================================

const synapseAgent = {
    // ... (o código do synapseAgent init e trackEvent continua o mesmo) ...
};

function inicializarMotorDeGatilhos(config) {
    // ... (a lógica dos gatilhos normais continua a mesma) ...
}

// --- NOVA FUNÇÃO PARA A BARRA DE CAMPANHA ---
function mostrarBarraDeContagem(campaignConfig, endDate) {
    const bar = document.createElement('div');
    bar.id = 'synapcortex-countdown-bar';
    bar.style.cssText = `
        position: fixed; top: 0; left: 0; width: 100%;
        background: linear-gradient(90deg, #C732D8, #00bfff);
        color: white; text-align: center; padding: 10px;
        font-size: 16px; font-weight: bold; z-index: 99999;
        font-family: sans-serif; box-shadow: 0 2px 5px rgba(0,0,0,0.3);
    `;
    
    const textSpan = document.createElement('span');
    textSpan.textContent = campaignConfig.countdown_bar_text || '';

    const timerSpan = document.createElement('span');
    timerSpan.id = 'synapcortex-timer';
    timerSpan.style.marginLeft = '10px';

    bar.appendChild(textSpan);
    bar.appendChild(timerSpan);
    document.body.prepend(bar);
    document.body.style.transform = `translateY(${bar.offsetHeight}px)`;


    const targetDate = new Date(endDate).getTime();

    const countdownInterval = setInterval(function() {
        const now = new Date().getTime();
        const distance = targetDate - now;

        if (distance < 0) {
            clearInterval(countdownInterval);
            timerSpan.textContent = "OFERTA ENCERRADA!";
            setTimeout(() => {
                document.body.removeChild(bar);
                document.body.style.transform = 'translateY(0px)';
            }, 3000);
            return;
        }

        const days = Math.floor(distance / (1000 * 60 * 60 * 24));
        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);

        timerSpan.textContent = `${hours.toString().padStart(2, '0')}h ${minutes.toString().padStart(2, '0')}m ${seconds.toString().padStart(2, '0')}s`;
    }, 1000);
}


// Auto-execução quando o script é carregado
if (synapseAgent.init()) {
    synapseAgent.trackEvent('pagina_visitada', { url: window.location.pathname, title: document.title });
    
    fetch(`${synapseAgent.backendUrl}/api/get-client-config?key=${synapseAgent.apiKey}`)
        .then(response => response.json())
        .then(config => {
            if (config && !config.error) {

                if (config.is_campaign_active) {
                    console.log("MODO BLACK FRIDAY ATIVO!", config.campaign_config);
                    mostrarBarraDeContagem(config.campaign_config, config.campaign_end_date);
                } else {
                    inicializarMotorDeGatilhos(config);
                }
            }
        })
        .catch(error => console.error("SynapCortex Spy: Falha ao obter configs.", error));
}