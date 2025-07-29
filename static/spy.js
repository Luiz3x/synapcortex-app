// Arquivo: spy.js
// Versão: 4.0 - "Agente de Campo"
// Descrição: O espião agora busca suas configurações via API Key e obedece às ordens do painel.

document.addEventListener('DOMContentLoaded', function() {

    // =================================================================================
    // MÓDULO 1: FERRAMENTAS DO ESPIÃO
    // =================================================================================

    function getApiKey() {
        // Encontra o próprio script na página pelo ID para ler a chave de API.
        const scriptTag = document.getElementById('synapcortex-spy-script');
        if (!scriptTag) {
            console.error("SynapCortex: O script de instalação não foi encontrado ou está sem o ID 'synapcortex-spy-script'.");
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

    function mostrarPopup(motivo) {
        if (popupMostradoNestaSessao) return;
        popupMostradoNestaSessao = true;
        console.log(`SynapCortex: Pop-up acionado! Motivo: ${motivo}`);
        
        // Esta lógica de buscar o texto do pop-up continua igual
        // e poderia ser integrada na outra chamada de API no futuro.
        fetch('/api/get-client-config?key=' + getApiKey())
            .then(response => response.json())
            .then(config => {
                const titulo = config.popup_titulo || "Temos uma oferta!";
                const mensagem = config.popup_mensagem || "Não perca esta chance.";
                document.getElementById('popup-titulo-display').innerText = titulo;
                document.getElementById('popup-mensagem-display').innerHTML = mensagem;
                document.getElementById('popup-espiao').style.display = 'flex';
            });
    }

    // =================================================================================
    // MÓDULO 3: O MOTOR DE GATILHOS (AGORA OBEDIENTE)
    // =================================================================================
    
    function inicializarMotorDeGatilhos(config) {
        console.log("SynapCortex: Ordens recebidas. Inicializando gatilhos...");
        console.log(config);

        // --- GATILHO 1: INTENÇÃO DE SAÍDA (Sempre ativo, mas com tática configurável) ---
        if (isMobileDevice()) {
            // A tática de "Botão Voltar" seria um "quarto" futuro. Por enquanto, focamos na principal.
            if (config.tatica_mobile === 'foco') {
                document.addEventListener('visibilitychange', () => {
                    if (document.visibilityState === 'hidden') mostrarPopup("Abandono Mobile");
                });
            }
        } else {
            document.addEventListener('mouseleave', event => {
                if (event.clientY <= 0) mostrarPopup("Abandono Desktop");
            });
        }

        // --- GATILHO 2: "BEM-VINDO DE VOLTA" (Opcional) ---
        // Ele só é ativado se o cliente ligou o botão no painel.
        if (config.ativar_quarto_bem_vindo) {
            const cookieVisita = 'synapcortex_visitou';
            if (document.cookie.includes(cookieVisita)) {
                console.log("SynapCortex: Visitante recorrente detectado e gatilho ATIVO.");
                // Aqui poderíamos ter um pop-up diferente no futuro, por enquanto, usamos o mesmo.
                mostrarPopup("Visitante Recorrente");
            } else {
                document.cookie = `${cookieVisita}=true; max-age=31536000; path=/`;
            }
        }
        
        // --- GATILHO 3: INATIVIDADE (Opcional) ---
        // Ele só é ativado se o cliente ligou o botão no painel.
        if (config.ativar_quarto_interessado) {
            let tempoInativo;
            const tempoLimite = 30000; // 30 segundos
            const reiniciarContador = () => {
                clearTimeout(tempoInativo);
                tempoInativo = setTimeout(() => mostrarPopup(`Inatividade`), tempoLimite);
            };
            ['load', 'mousemove', 'keydown', 'touchstart', 'click'].forEach(evento => window.addEventListener(evento, reiniciarContador, false));
            console.log("SynapCortex: Gatilho de inatividade ATIVO.");
        }
    }

    // =================================================================================
    // MÓDULO CENTRAL: O "RÁDIO" DE COMUNICAÇÃO
    // =================================================================================
    
    function iniciarComunicacao() {
        const apiKey = getApiKey();
        if (!apiKey) return; // Se não tem chave, o espião não faz nada.

        // O espião "liga" para a base para pedir as configurações
        fetch(`/api/get-client-config?key=${apiKey}`)
            .then(response => {
                if (!response.ok) throw new Error('Chave de API inválida ou erro no servidor.');
                return response.json();
            })
            .then(config => {
                // Com as configurações em mãos, ele inicializa os gatilhos corretos.
                inicializarMotorDeGatilhos(config);
            })
            .catch(error => {
                console.error("SynapCortex: Falha ao obter configurações.", error);
            });
    }

    // --- INICIALIZAÇÃO GERAL ---
    iniciarComunicacao();
    
    // (O restante do código para o modal de login, formulários, etc. continua o mesmo)
    // ... COLE O RESTANTE DO CÓDIGO DO SPY.JS (MÓDULO 4 E 5) AQUI ...
});