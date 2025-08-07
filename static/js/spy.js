// =================================================================================
// SYNAPCORTEX - SCRIPT MESTRE (AGENTE SYNAPSE)
// Versão 2.1 - COMPLETO E CONSOLIDADO PARA TODAS AS PÁGINAS
// =================================================================================

document.addEventListener('DOMContentLoaded', function() {
    
    // -----------------------------------------------------------------------------
    // PARTE 1: LÓGICA DA PÁGINA PRINCIPAL (index.html)
    // -----------------------------------------------------------------------------
    const openLoginRegisterModalBtn = document.getElementById('openLoginRegisterModal');
    if (openLoginRegisterModalBtn) {
        openLoginRegisterModalBtn.addEventListener('click', function() {
            window.location.href = '/login';
        });
    }

    const demoLoginBtn = document.getElementById('demoLoginBtn');
    if (demoLoginBtn) {
        demoLoginBtn.addEventListener('click', function() {
            window.location.href = '/login';
        });
    }

    const ctx = document.getElementById('graficoDemonstracao');
    if (ctx) {
        const labels = ['-50s', '-40s', '-30s', '-20s', '-10s', 'Agora'];
        const data = { labels: labels, datasets: [{ label: 'Clientes Recuperados', backgroundColor: 'rgba(0, 204, 255, 0.2)', borderColor: 'rgba(0, 204, 255, 1)', data: [65, 59, 80, 81, 56, 55], fill: true, tension: 0.4 }] };
        const config = { type: 'line', data: data, options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { color: '#bbbbbb' }, grid: { color: 'rgba(255, 255, 255, 0.1)' } }, x: { ticks: { color: '#bbbbbb' }, grid: { display: false } } } } };
        const meuGrafico = new Chart(ctx, config);
        setInterval(() => {
            const novoDado = Math.floor(Math.random() * 55) + 40;
            meuGrafico.data.datasets[0].data.shift();
            meuGrafico.data.datasets[0].data.push(novoDado);
            meuGrafico.update();
        }, 2000);
    }

    // -----------------------------------------------------------------------------
    // PARTE 2: LÓGICA DO ESPIÃO (PARA SITES DE CLIENTES)
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
            
            console.log("SynapCortex Agente: Inicializado. Visitante ID:", this.visitorId);
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
            }).catch(err => console.error("SynapCortex Agente: Falha ao enviar relatório.", err));
        }
    };

    let popupMostradoNestaSessao = false;
    function mostrarPopup(motivo, titulo, mensagem) {
        if (popupMostradoNestaSessao) return;
        popupMostradoNestaSessao = true;
        
        console.log(`SynapCortex: Pop-up acionado! Motivo: ${motivo}`);
        synapseAgent.trackEvent('popup_exibido', { gatilho: motivo });

        const popupDiv = document.createElement('div');
        popupDiv.innerHTML = `<div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.7); display: flex; justify-content: center; align-items: center; z-index: 9999; font-family: sans-serif;"><div style="background-color: #fff; color: #333; padding: 20px 40px; border-radius: 8px; text-align: center; max-width: 400px; position: relative;"><button class="fechar-btn-synapcortex" style="position: absolute; top: 10px; right: 15px; background: none; border: none; font-size: 24px; cursor: pointer; color: #333;">&times;</button><h2>${titulo}</h2><p>${mensagem}</p></div></div>`;
        document.body.appendChild(popupDiv);
        popupDiv.querySelector('.fechar-btn-synapcortex').addEventListener('click', () => { document.body.removeChild(popupDiv); });
    }

    function inicializarMotorDeGatilhos(config) {
        const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);

        if (config.ativar_abandono) {
            if (isMobile) {
                document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'hidden' && !popupMostradoNestaSessao) { mostrarPopup("Abandono Mobile", config.popup_titulo, config.popup_mensagem); }});
            } else {
                document.addEventListener('mouseleave', event => { if (event.clientY <= 0 && !popupMostradoNestaSessao) { mostrarPopup("Abandono Desktop", config.popup_titulo, config.popup_mensagem); }});
            }
        }
        if (config.ativar_quarto_bem_vindo) {
            const cookieName = 'synapcortex_visitou';
            if (document.cookie.includes(cookieName)) { mostrarPopup("Visitante Recorrente", config.popup_titulo, config.msg_bem_vindo); }
            document.cookie = `${cookieName}=true; max-age=31536000; path=/`;
        }
        if (config.ativar_quarto_interessado) {
            let inactivityTimer;
            const resetTimer = () => { clearTimeout(inactivityTimer); inactivityTimer = setTimeout(() => { mostrarPopup("Inatividade", config.popup_titulo, config.msg_interessado); }, 30000); };
            window.onload = resetTimer; document.onmousemove = resetTimer; document.onkeydown = resetTimer;
        }
    }

    // --- BLOCO DE EXECUÇÃO ---
    // O script primeiro tenta agir como um espião.
    if (synapseAgent.init()) {
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