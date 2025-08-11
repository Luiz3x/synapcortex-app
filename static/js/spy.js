// =================================================================================
// SYNAPCORTEX - SCRIPT MESTRE (AGENTE SYNAPSE)
// Versão 2.3 - Relatório de Page View enriquecido com o título da página.
// =================================================================================

document.addEventListener('DOMContentLoaded', function() {
    
    // -----------------------------------------------------------------------------
    // PARTE 1: LÓGICA DO NOSSO SITE (PÁGINA PRINCIPAL E DASHBOARD)
    // -----------------------------------------------------------------------------
    // (Esta seção contém o código para os botões da página inicial, o gráfico,
    // o formulário de salvar configurações, etc. Ela não é executada no site do cliente)
    if (document.getElementById('openLoginRegisterModal')) {
        // ... (toda a lógica que já temos para o nosso site, como os modais e botões)
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
        // ... (código para criar e mostrar o HTML do pop-up)
    }

    function inicializarMotorDeGatilhos(config) {
        // ... (código dos gatilhos de abandono, bem-vindo, etc.)
    }

    // --- BLOCO DE EXECUÇÃO PRINCIPAL DO AGENTE ---
    if (synapseAgent.init()) {
        
        // [ALTERAÇÃO] O Agente envia seu primeiro relatório de vigilância enriquecido com o título da página.
        synapseAgent.trackEvent('pagina_visitada', { url: window.location.pathname, title: document.title });

        // O Agente busca as ordens na central para os gatilhos de pop-up
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