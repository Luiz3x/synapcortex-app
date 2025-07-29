// Arquivo: spy.js
// Versão: 5.0 - "Voz Personalizada"
// Descrição: O espião usa as mensagens personalizadas para cada gatilho.

document.addEventListener('DOMContentLoaded', function() {

    // =================================================================================
    // MÓDULO 1: FERRAMENTAS DO ESPIÃO
    // =================================================================================

    function getApiKey() {
        const scriptTag = document.getElementById('synapcortex-spy-script');
        if (!scriptTag) {
            console.error("SynapCortex: O ID 'synapcortex-spy-script' não foi encontrado na tag do script.");
            return null;
        }
        const scriptUrl = new URL(scriptTag.src);
        return scriptUrl.searchParams.get('key');
    }

    function isMobileDevice() {
        return (typeof window.orientation !== "undefined") || (navigator.userAgent.indexOf('IEMobile') !== -1);
    }

    // =================================================================================
    // MÓDULO 2: O POP-UP (A AÇÃO FINAL)
    // =================================================================================
    
    let popupMostradoNestaSessao = false;

    function mostrarPopup(motivo, titulo, mensagem) {
        if (popupMostradoNestaSessao) return;
        popupMostradoNestaSessao = true;
        console.log(`SynapCortex: Pop-up acionado! Motivo: ${motivo}`);
        
        document.getElementById('popup-titulo-display').innerText = titulo;
        document.getElementById('popup-mensagem-display').innerHTML = mensagem;
        document.getElementById('popup-espiao').style.display = 'flex';
    }

    // =================================================================================
    // MÓDULO 3: O MOTOR DE GATILHOS (AGORA COM VOZ PERSONALIZADA)
    // =================================================================================
    
    function inicializarMotorDeGatilhos(config) {
        console.log("SynapCortex: Ordens recebidas. Inicializando gatilhos...");

        const tituloPadrao = config.popup_titulo || "Temos uma oferta!";
        const mensagemPadrao = config.popup_mensagem || "Não perca esta chance.";

        // --- GATILHO 1: INTENÇÃO DE SAÍDA ---
        if (isMobileDevice()) {
            if (config.tatica_mobile === 'foco') {
                document.addEventListener('visibilitychange', () => {
                    if (document.visibilityState === 'hidden') mostrarPopup("Abandono Mobile", tituloPadrao, mensagemPadrao);
                });
            }
        } else {
            document.addEventListener('mouseleave', event => {
                if (event.clientY <= 0) mostrarPopup("Abandono Desktop", tituloPadrao, mensagemPadrao);
            });
        }

        // --- GATILHO 2: "BEM-VINDO DE VOLTA" ---
        if (config.ativar_quarto_bem_vindo) {
            const cookieVisita = 'synapcortex_visitou';
            if (document.cookie.includes(cookieVisita)) {
                // >>> MUDANÇA: Usa a mensagem personalizada se ela existir, senão usa a padrão.
                const mensagemBemVindo = config.msg_bem_vindo || mensagemPadrao;
                const tituloBemVindo = (config.msg_bem_vindo && config.popup_titulo) ? config.popup_titulo : tituloPadrao;
                mostrarPopup("Visitante Recorrente", tituloBemVindo, mensagemBemVindo);
            } else {
                document.cookie = `${cookieVisita}=true; max-age=31536000; path=/`;
            }
        }
        
        // --- GATILHO 3: INATIVIDADE ---
        if (config.ativar_quarto_interessado) {
            let tempoInativo;
            const tempoLimite = 30000; // 30 segundos
            const reiniciarContador = () => {
                clearTimeout(tempoInativo);
                tempoInativo = setTimeout(() => {
                    // >>> MUDANÇA: Usa a mensagem personalizada se ela existir, senão usa a padrão.
                    const mensagemInteressado = config.msg_interessado || mensagemPadrao;
                    const tituloInteressado = (config.msg_interessado && config.popup_titulo) ? config.popup_titulo : tituloPadrao;
                    mostrarPopup(`Inatividade`, tituloInteressado, mensagemInteressado);
                }, tempoLimite);
            };
            ['load', 'mousemove', 'keydown', 'touchstart', 'click'].forEach(evento => window.addEventListener(evento, reiniciarContador, false));
        }
    }

    // =================================================================================
    // MÓDULO 4: LÓGICA DA PÁGINA (GRÁFICO, MODAL, FORMULÁRIOS)
    // =================================================================================

    function inicializarLogicaDaPagina() {
        const ctx = document.getElementById('graficoDemonstracao');
        if (ctx) {
            // ... (código do gráfico continua o mesmo)
        }
        // ... (código do modal de login e formulários continua o mesmo)
    }

    // =================================================================================
    // MÓDULO CENTRAL E INICIALIZAÇÃO GERAL
    // =================================================================================
    
    inicializarLogicaDaPagina();

    const apiKey = getApiKey();
    if (apiKey) {
        fetch(`/api/get-client-config?key=${apiKey}`)
            .then(response => {
                if (!response.ok) throw new Error('Chave de API inválida ou erro no servidor.');
                return response.json();
            })
            .then(config => {
                inicializarMotorDeGatilhos(config);
            })
            .catch(error => {
                console.error("SynapCortex: Falha ao obter configurações.", error);
            });
    }
});