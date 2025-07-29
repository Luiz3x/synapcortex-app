// Arquivo: spy.js
// Versão: 3.2 - "Cérebro" (com correção do bug do gráfico)
// Descrição: Script espião completo com todas as funcionalidades restauradas e inteligência avançada.

document.addEventListener('DOMContentLoaded', function() {

    // =================================================================================
    // MÓDULO 1: FERRAMENTAS DO ESPIÃO
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
    // MÓDULO 2: O POP-UP (A AÇÃO FINAL)
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
    // MÓDULO 3: O MOTOR DE GATILHOS
    // =================================================================================
    
    function inicializarMotorDeGatilhos() {
        console.log("SynapCortex: Motor de inteligência inicializado.");

        if (isMobileDevice()) {
            document.addEventListener('visibilitychange', () => {
                if (document.visibilityState === 'hidden') mostrarPopup("Abandono Mobile");
            });
        } else {
            document.addEventListener('mouseleave', event => {
                if (event.clientY <= 0) mostrarPopup("Abandono Desktop");
            });
        }

        if (!getCookie('synapcortex_visitou')) {
            setCookie('synapcortex_visitou', 'true', 365);
        }

        let tempoInativo;
        const tempoLimite = 30000;
        const reiniciarContador = () => {
            clearTimeout(tempoInativo);
            tempoInativo = setTimeout(() => mostrarPopup(`Inatividade`), tempoLimite);
        };
        ['load', 'mousemove', 'keydown', 'touchstart', 'click'].forEach(evento => window.addEventListener(evento, reiniciarContador, false));
    }
    
    // =================================================================================
    // MÓDULO 4: GRÁFICO DE DEMONSTRAÇÃO (CÓDIGO RESTAURADO)
    // =================================================================================

    function inicializarGraficoDemo() {
        const ctx = document.getElementById('graficoDemonstracao');
        if (!ctx) return; // Se o gráfico não está na página, não faz nada.

        const labels = ['-50s', '-40s', '-30s', '-20s', '-10s', 'Agora'];
        const data = {
            labels: labels,
            datasets: [{
                label: 'Clientes Recuperados',
                backgroundColor: 'rgba(0, 204, 255, 0.2)',
                borderColor: 'rgba(0, 204, 255, 1)',
                data: [65, 59, 80, 81, 56, 55],
                fill: true,
                tension: 0.4
            }]
        };

        const config = {
            type: 'line',
            data: data,
            options: {
                responsive: true,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, ticks: { color: '#bbbbbb' }, grid: { color: 'rgba(255, 255, 255, 0.1)' } },
                    x: { ticks: { color: '#bbbbbb' }, grid: { display: false } }
                }
            }
        };

        const meuGrafico = new Chart(ctx, config);

        setInterval(function() {
            const novoDado = Math.floor(Math.random() * 55) + 40;
            meuGrafico.data.datasets[0].data.shift();
            meuGrafico.data.datasets[0].data.push(novoDado);
            meuGrafico.update();
        }, 2000);
    }

    // =================================================================================
    // MÓDULO 5: LÓGICA DA PÁGINA (MODAL, FORMULÁRIOS, ETC.)
    // =================================================================================

    const fecharPopupBtn = document.getElementById('fechar-popup');
    if (fecharPopupBtn) {
        fecharPopupBtn.addEventListener('click', () => {
            document.getElementById('popup-espiao').style.display = 'none';
        });
    }

    const modal = document.getElementById('loginRegisterModal');
    const openModalBtn = document.getElementById('openLoginRegisterModal');
    const closeButton = document.querySelector('.modal .close-button');
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
    window.onclick = event => { if (event.target == modal) modal.style.display = 'none'; };

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
            const formData = new FormData(loginForm);
            fetch("/login", {
                method: 'POST',
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                body: new URLSearchParams(formData)
            })
            .then(response => response.json().then(data => ({ ok: response.ok, data })))
            .then(({ ok, data }) => {
                if (ok) window.location.href = data.redirect_url;
                else throw data;
            })
            .catch(error => {
                loginErrorMessage.textContent = error.message || 'Erro.';
                loginErrorMessage.style.display = 'block';
            });
        });
    }

    if(registerForm) {
        registerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(registerForm);
            fetch("/registrar", {
                method: 'POST',
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                body: new URLSearchParams(formData)
            })
            .then(response => response.json().then(data => ({ ok: response.ok, data })))
            .then(({ ok, data }) => {
                if (ok) window.location.href = data.redirect_url;
                else throw data;
            })
            .catch(error => {
                registerErrorMessage.textContent = error.message || 'Erro.';
                registerErrorMessage.style.display = 'block';
            });
        });
    }

    // --- INICIALIZAÇÃO GERAL ---
    inicializarMotorDeGatilhos();
    inicializarGraficoDemo();
});