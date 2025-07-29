// Arquivo: spy.js
// Versão: 3.1 - "Cérebro" (com correção de bug do modal)
// Descrição: Script espião da SynapCortex com inteligência avançada, múltiplos gatilhos,
// gerenciamento de cookies e preparação para o motor de regras.

document.addEventListener('DOMContentLoaded', function() {

    // =================================================================================
    // MÓDULO 1: FERRAMENTAS DO ESPIÃO (Funções Auxiliares)
    // =================================================================================

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

    function isMobileDevice() {
        return (typeof window.orientation !== "undefined") || (navigator.userAgent.indexOf('IEMobile') !== -1);
    }

    // =================================================================================
    // MÓDULO 2: O POP-UP (A Ação Final)
    // =================================================================================
    
    let popupMostradoNestaSessao = false;

    function mostrarPopup(motivo) {
        if (popupMostradoNestaSessao) return;
        popupMostradoNestaSessao = true;
        
        console.log(`SynapCortex: Pop-up acionado! Motivo: ${motivo}`);

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

        if (isMobileDevice()) {
            document.addEventListener('visibilitychange', function() {
                if (document.visibilityState === 'hidden') {
                    mostrarPopup("Abandono Mobile (Mudança de Aba/App)");
                }
            });
        } else {
            document.addEventListener('mouseleave', function(event) {
                if (event.clientY <= 0) {
                    mostrarPopup("Abandono Desktop (Mouse no Topo)");
                }
            });
        }

        const cookieVisita = 'synapcortex_visitou';
        if (!getCookie(cookieVisita)) {
            setCookie(cookieVisita, 'true', 365);
        }

        let tempoInativo;
        const tempoLimite = 30000;

        function reiniciarContadorDeInatividade() {
            clearTimeout(tempoInativo);
            tempoInativo = setTimeout(() => {
                mostrarPopup(`Inatividade (${tempoLimite / 1000}s)`);
            }, tempoLimite);
        }
        
        window.onload = reiniciarContadorDeInatividade;
        document.onmousemove = reiniciarContadorDeInatividade;
        document.onkeydown = reiniciarContadorDeInatividade;
        document.ontouchstart = reiniciarContadorDeInatividade;
        document.onclick = reiniciarContadorDeInatividade;
    }

    // --- INICIALIZAÇÃO GERAL ---
    inicializarMotorDeGatilhos();

    // =================================================================================
    // MÓDULO 4: LÓGICA DA PÁGINA (Modal, Formulários, etc. - CÓDIGO RESTAURADO)
    // =================================================================================

    const fecharPopupBtn = document.getElementById('fechar-popup');
    if (fecharPopupBtn) {
        fecharPopupBtn.addEventListener('click', function() {
            document.getElementById('popup-espiao').style.display = 'none';
        });
    }

    // --- Lógica do Modal de Login/Cadastro (AGORA CORRETA E COMPLETA) ---
    const modal = document.getElementById('loginRegisterModal');
    const openModalBtn = document.getElementById('openLoginRegisterModal');
    const closeButton = document.querySelector('.modal .close-button'); // Seletor mais específico
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const loginErrorMessage = document.getElementById('loginErrorMessage');
    const registerErrorMessage = document.getElementById('registerErrorMessage');

    if (openModalBtn) {
        openModalBtn.onclick = () => { modal.style.display = 'flex'; };
    }
    if (closeButton) {
        closeButton.onclick = () => { modal.style.display = 'none'; };
    }
    window.onclick = (event) => { if (event.target == modal) { modal.style.display = 'none'; } };

    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            this.classList.add('active');
            document.getElementById(this.dataset.tab + 'Tab').classList.add('active');
        });
    });

    if(loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            loginErrorMessage.style.display = 'none';
            const formData = new FormData(loginForm);
            fetch("/login", {
                method: 'POST',
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                body: new URLSearchParams(formData)
            })
            .then(response => response.json().then(data => ({ ok: response.ok, data })))
            .then(({ ok, data }) => {
                if (ok) {
                    window.location.href = data.redirect_url;
                } else {
                    throw data;
                }
            })
            .catch(error => {
                loginErrorMessage.textContent = error.message || 'Erro na comunicação.';
                loginErrorMessage.style.display = 'block';
            });
        });
    }

    if(registerForm) {
        registerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            registerErrorMessage.style.display = 'none';
            const formData = new FormData(registerForm);
            fetch("/registrar", {
                method: 'POST',
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                body: new URLSearchParams(formData)
            })
            .then(response => response.json().then(data => ({ ok: response.ok, data })))
            .then(({ ok, data }) => {
                if (ok) {
                    window.location.href = data.redirect_url;
                } else {
                    throw data;
                }
            })
            .catch(error => {
                registerErrorMessage.textContent = error.message || 'Erro na comunicação.';
                registerErrorMessage.style.display = 'block';
            });
        });
    }
});