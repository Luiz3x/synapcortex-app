// =================================================================================
// SYNAPCORTEX - SCRIPT MESTRE (AGENTE SYNAPSE + LÓGICA DO SITE)
// Versão 2.6 - Versão definitiva com todas as lógicas implementadas.
// =================================================================================

document.addEventListener('DOMContentLoaded', function() {
    
    // -----------------------------------------------------------------------------
    // PARTE 1: LÓGICA DO NOSSO SITE (PÁGINA PRINCIPAL E DASHBOARD)
    // -----------------------------------------------------------------------------
    const loginRegisterModal = document.getElementById('loginRegisterModal');
    if (loginRegisterModal) {
        // ... (código do modal de login/registro que já está funcionando)
    }

    // -----------------------------------------------------------------------------
    // PARTE 2: O AGENTE SYNAPSE E O ESPIÃO (PARA SITES DE CLIENTES)
    // -----------------------------------------------------------------------------
    const synapseAgent = {
        apiKey: null,
        backendUrl: null,
        visitorId: null,
        init: function() { /* ... (código de inicialização que já está funcionando) */ },
        trackEvent: function(eventName, eventData = {}) { /* ... (código de track que já está funcionando) */ }
    };

    // [IMPLEMENTAÇÃO COMPLETA] - LÓGICA DE EXIBIÇÃO DO POP-UP
    let popupMostradoNestaSessao = false;
    function mostrarPopup(motivo, titulo, mensagem) {
        if (popupMostradoNestaSessao) return;
        popupMostradoNestaSessao = true;
        
        // >>> A LINHA CRÍTICA QUE FALTAVA <<<
        synapseAgent.trackEvent('popup_exibido', { gatilho: motivo });

        // Cria o HTML do pop-up dinamicamente
        const popupContainer = document.createElement('div');
        popupContainer.style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; z-index: 9999;';
        
        const popupContent = document.createElement('div');
        popupContent.style.cssText = 'background-color: white; padding: 20px 30px; border-radius: 8px; text-align: center; max-width: 400px;';
        
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

        closeButton.onclick = () => {
            document.body.removeChild(popupContainer);
        };
        popupContainer.onclick = (e) => {
            if(e.target === popupContainer){
                 document.body.removeChild(popupContainer);
            }
        }
    }

    // [IMPLEMENTAÇÃO COMPLETA] - LÓGICA DOS GATILHOS
    function inicializarMotorDeGatilhos(config) {
        // --- Gatilho de Abandono de Site ---
        if (config.ativar_abandono) {
            document.addEventListener('mouseleave', function(e) {
                // Tenta detectar se o mouse está saindo pela parte de cima da janela
                if (e.clientY <= 0) {
                    mostrarPopup(
                        'abandono_de_site', 
                        config.popup_titulo || 'Não vá embora!', 
                        config.popup_mensagem || 'Temos uma oferta especial para você.'
                    );
                }
            });
        }
        // Futuramente, outros gatilhos (bem-vindo de volta, etc.) virão aqui.
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

// Para manter o código mais limpo, estou omitindo a repetição das Partes 1 e do objeto synapseAgent, 
// que já sabemos que estão funcionando. O código final deve conter todas as partes.
// Se precisar que eu envie um único bloco de código com TUDO junto, me avise.