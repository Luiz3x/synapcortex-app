// Arquivo: spy.js
// Versão: 3.0 - "Cérebro"
// Descrição: Script espião da SynapCortex com inteligência avançada, múltiplos gatilhos,
// gerenciamento de cookies e preparação para o motor de regras.

document.addEventListener('DOMContentLoaded', function() {

    // =================================================================================
    // MÓDULO 1: FERRAMENTAS DO ESPIÃO (Funções Auxiliares)
    // =================================================================================

    // --- Funções para Manipulação de Cookies ---
    // O espião agora tem memória de longo prazo.
    function setCookie(name, value, days) {
        let expires = "";
        if (days) {
            const date = new Date();
            date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
            expires = "; expires=" + date.toUTCString();
        }
        document.cookie = name + "=" + (value || "") + expires + "; path=/";
    }

    function getCookie(name) {
        const nameEQ = name + "=";
        const ca = document.cookie.split(';');
        for(let i = 0; i < ca.length; i++) {
            let c = ca[i];
            while (c.charAt(0) === ' ') c = c.substring(1, c.length);
            if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
        }
        return null;
    }

    // --- Detecção de Dispositivo ---
    function isMobileDevice() {
        return (typeof window.orientation !== "undefined") || (navigator.userAgent.indexOf('IEMobile') !== -1);
    }

    // =================================================================================
    // MÓDULO 2: O POP-UP (A Ação Final)
    // =================================================================================
    
    let popupMostradoNestaSessao = false;

    function mostrarPopup(motivo) {
        // O espião só age uma vez por visita para não ser chato.
        if (popupMostradoNestaSessao) return;
        popupMostradoNestaSessao = true;
        
        console.log(`SynapCortex: Pop-up acionado! Motivo: ${motivo}`);

        // A lógica de buscar a configuração do pop-up continua a mesma
        fetch('/api/get-config')
            .then(response => response.json())
            .then(config => {
                if (config.titulo && config.mensagem) {
                    document.getElementById('popup-titulo-display').innerText = config.titulo;
                    document.getElementById('popup-mensagem-display').innerHTML = config.mensagem;
                    document.getElementById('popup-espiao').style.display = 'flex';
                }
            })
            .catch(error => console.error('Erro ao buscar a configuração do pop-up:', error));
    }

    // =================================================================================
    // MÓDULO 3: O MOTOR DE GATILHOS (O CORAÇÃO DA INTELIGÊNCIA)
    // =================================================================================
    
    function inicializarMotorDeGatilhos() {
        console.log("SynapCortex: Motor de inteligência inicializado.");

        // --- GATILHO 1: INTENÇÃO DE SAÍDA (Desktop & Mobile) ---
        if (isMobileDevice()) {
            // Tática Mobile: Mudança de Foco
            document.addEventListener('visibilitychange', function() {
                if (document.visibilityState === 'hidden') {
                    mostrarPopup("Abandono Mobile (Mudança de Aba/App)");
                }
            });
        } else {
            // Tática Desktop: Saída com o Mouse
            document.addEventListener('mouseleave', function(event) {
                if (event.clientY <= 0) {
                    mostrarPopup("Abandono Desktop (Mouse no Topo)");
                }
            });
        }

        // --- GATILHO 2: VISITANTE RECORRENTE (O Quarto "Bem-vindo de Volta") ---
        // Aqui usamos a memória (cookies) do espião.
        const cookieVisita = 'synapcortex_visitou';
        if (getCookie(cookieVisita)) {
            // Se o cookie existe, o cliente já esteve aqui.
            // No futuro, podemos mostrar um pop-up específico aqui.
            console.log("SynapCortex: Visitante recorrente detectado.");
            // Exemplo de como poderíamos agir:
            // mostrarPopup("Visitante Recorrente"); 
            // Por enquanto, apenas registramos.
        } else {
            // Se o cookie não existe, é a primeira visita.
            // Criamos o cookie para lembrar dele no futuro.
            console.log("SynapCortex: Primeira visita registrada. Marcando o visitante.");
            setCookie(cookieVisita, 'true', 365); // Lembra do visitante por 1 ano.
        }

        // --- GATILHO 3: TEMPO DE INATIVIDADE (O Quarto "Interessado") ---
        let tempoInativo;
        const tempoLimite = 30000; // 30 segundos

        function reiniciarContadorDeInatividade() {
            clearTimeout(tempoInativo);
            tempoInativo = setTimeout(() => {
                // O usuário ficou inativo pelo tempo limite.
                mostrarPopup(`Inatividade (${tempoLimite / 1000}s)`);
            }, tempoLimite);
        }
        
        // Qualquer uma dessas ações reinicia o contador.
        window.onload = reiniciarContadorDeInatividade;
        document.onmousemove = reiniciarContadorDeInatividade;
        document.onkeydown = reiniciarContadorDeInatividade;
        document.ontouchstart = reiniciarContadorDeInatividade; // Para toques no celular
        document.onclick = reiniciarContadorDeInatividade;

        console.log(`SynapCortex: Gatilho de inatividade configurado para ${tempoLimite / 1000} segundos.`);
    }

    // --- INICIALIZAÇÃO GERAL ---
    inicializarMotorDeGatilhos();

    // =================================================================================
    // MÓDULO 4: LÓGICA DA PÁGINA (Modal, Formulários, etc. - Sem alterações)
    // =================================================================================

    const fecharPopupBtn = document.getElementById('fechar-popup');
    if (fecharPopupBtn) {
        fecharPopupBtn.addEventListener('click', function() {
            document.getElementById('popup-espiao').style.display = 'none';
        });
    }

    const modal = document.getElementById('loginRegisterModal');
    const openModalBtn = document.getElementById('openLoginRegisterModal');
    // ... (O restante do seu código para modal e formulários continua aqui, exatamente como estava)
    // ...
});