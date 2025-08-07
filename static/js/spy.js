// =================================================================================
// SYNAPCORTEX - SCRIPT MESTRE (AGENTE SYNAPSE)
// Versão 2.0 - Com rastreamento de eventos para o Módulo de Analytics
// =================================================================================

document.addEventListener('DOMContentLoaded', function() {
    
    // --- [NOVO] MÓDULO DE INTELIGÊNCIA DO AGENTE ---
    const synapseAgent = {
        apiKey: null,
        backendUrl: null,
        visitorId: null,

        // Habilidade 1: Inicialização e Memória Fotográfica
        init: function() {
            const scriptTag = document.getElementById('synapcortex-spy-script');
            if (!scriptTag) return false;

            this.backendUrl = scriptTag.dataset.backendUrl || window.location.origin;
            const scriptUrl = new URL(scriptTag.src);
            this.apiKey = scriptUrl.searchParams.get('key');

            if (!this.apiKey) return false;

            // Cria ou recupera a identidade única do visitante
            let storedVisitorId = localStorage.getItem('synapcortex_visitor_id');
            if (!storedVisitorId) {
                storedVisitorId = Date.now() + '-' + Math.random().toString(36).substr(2, 9);
                localStorage.setItem('synapcortex_visitor_id', storedVisitorId);
            }
            this.visitorId = storedVisitorId;
            
            console.log("SynapCortex Agente: Inicializado. Visitante ID:", this.visitorId);
            return true;
        },

        // Habilidade 2: Comunicação Secreta (Enviar Relatórios)
        trackEvent: function(eventName, eventData = {}) {
            if (!this.apiKey) return;

            const payload = {
                apiKey: this.apiKey,
                visitorId: this.visitorId,
                eventName: eventName,
                eventData: eventData
            };

            // Envia o relatório para a nossa central de inteligência
            fetch(`${this.backendUrl}/api/track`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
                keepalive: true // Garante que a requisição seja enviada mesmo se a página fechar
            }).catch(err => console.error("SynapCortex Agente: Falha ao enviar relatório.", err));
        }
    };


    // --- MÓDULO DE AÇÃO (O "VIGIA") ---
    
    let popupMostradoNestaSessao = false;
    function mostrarPopup(motivo, titulo, mensagem) {
        if (popupMostradoNestaSessao) return;
        popupMostradoNestaSessao = true;
        
        console.log(`SynapCortex: Pop-up acionado! Motivo: ${motivo}`);
        
        // [NOVO] O Agente envia seu primeiro relatório!
        synapseAgent.trackEvent('popup_exibido', { gatilho: motivo });

        const popupDiv = document.createElement('div');
        // ... (código HTML do pop-up continua o mesmo)
        document.body.appendChild(popupDiv);
        // ... (lógica de fechar o pop-up continua a mesma)
    }

    function inicializarMotorDeGatilhos(config) {
        // ... (toda a lógica dos gatilhos de abandono, bem-vindo de volta, etc. continua a mesma)
    }


    // --- BLOCO DE EXECUÇÃO PRINCIPAL ---

    // Inicializa o Agente Synapse. Se ele não encontrar uma API Key, ele sabe que não está em um site de cliente.
    if (synapseAgent.init()) {
        // Se a inicialização for um sucesso, estamos no site de um cliente.
        // O Agente busca as ordens na central.
        fetch(`${synapseAgent.backendUrl}/api/get-client-config?key=${synapseAgent.apiKey}`)
            .then(response => response.json())
            .then(config => {
                if (config && !config.error) {
                    console.log("SynapCortex: Ordens recebidas. Inicializando gatilhos...");
                    inicializarMotorDeGatilhos(config);
                } else {
                    console.error("SynapCortex: Configurações inválidas recebidas.");
                }
            })
            .catch(error => {
                console.error("SynapCortex: Falha ao obter configurações.", error);
            });
    }

    // Se o Agente não inicializou, o resto do script (lógica do nosso painel, site principal) é carregado.
    // ... (código do gráfico, do formulário de salvar, da central de ajuda, etc. que já temos)
});