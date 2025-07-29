// Arquivo: spy.js
// Versão: 4.1 - "Agente de Campo" (com todas as lógicas da página restauradas)
// Descrição: O espião busca suas configurações via API Key e obedece às ordens do painel.

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

    function mostrarPopup(motivo, config) {
        if (popupMostradoNestaSessao) return;
        popupMostradoNestaSessao = true;
        console.log(`SynapCortex: Pop-up acionado! Motivo: ${motivo}`);
        
        const titulo = config.popup_titulo || "Temos uma oferta!";
        const mensagem = config.popup_mensagem || "Não perca esta chance.";
        document.getElementById('popup-titulo-display').innerText = titulo;
        document.getElementById('popup-mensagem-display').innerHTML = mensagem;
        document.getElementById('popup-espiao').style.display = 'flex';
    }

    // =================================================================================
    // MÓDULO 3: O MOTOR DE GATILHOS (AGORA OBEDIENTE)
    // =================================================================================
    
    function inicializarMotorDeGatilhos(config) {
        console.log("SynapCortex: Ordens recebidas. Inicializando gatilhos...");

        if (isMobileDevice()) {
            if (config.tatica_mobile === 'foco') { // Apenas um exemplo, tática 'voltar' a ser implementada
                document.addEventListener('visibilitychange', () => {
                    if (document.visibilityState === 'hidden') mostrarPopup("Abandono Mobile", config);
                });
            }
        } else {
            document.addEventListener('mouseleave', event => {
                if (event.clientY <= 0) mostrarPopup("Abandono Desktop", config);
            });
        }

        if (config.ativar_quarto_bem_vindo) {
            // Lógica do quarto "Bem-vindo de Volta" a ser implementada aqui
            console.log("SynapCortex: Gatilho 'Bem-vindo de Volta' está ATIVO (lógica pendente).");
        }
        
        if (config.ativar_quarto_interessado) {
            let tempoInativo;
            const tempoLimite = 30000;
            const reiniciarContador = () => {
                clearTimeout(tempoInativo);
                tempoInativo = setTimeout(() => mostrarPopup(`Inatividade`, config), tempoLimite);
            };
            ['load', 'mousemove', 'keydown', 'touchstart', 'click'].forEach(evento => window.addEventListener(evento, reiniciarContador, false));
            console.log("SynapCortex: Gatilho de inatividade ATIVO.");
        }
    }

    // =================================================================================
    // MÓDULO 4: LÓGICA DA PÁGINA (GRÁFICO, MODAL, FORMULÁRIOS)
    // =================================================================================

    function inicializarLogicaDaPagina() {
        // --- GRÁFICO DE DEMONSTRAÇÃO ---
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

        // --- MODAL DE LOGIN/CADASTRO ---
        const modal = document.getElementById('loginRegisterModal');
        const openModalBtn = document.getElementById('openLoginRegisterModal');
        const closeButton = document.querySelector('.modal .close-button');
        const tabButtons = document.querySelectorAll('.tab-button');
        const tabContents = document.querySelectorAll('.tab-content');
        const loginForm = document.getElementById('loginForm');
        const registerForm = document.getElementById('registerForm');
        const loginErrorMessage = document.getElementById('loginErrorMessage');
        const registerErrorMessage = document.getElementById('registerErrorMessage');

        if (openModalBtn) { openModalBtn.onclick = () => { modal.style.display = 'flex'; }; }
        if (closeButton) { closeButton.onclick = () => { modal.style.display = 'none'; }; }
        window.onclick = event => { if (event.target == modal) modal.style.display = 'none'; };

        tabButtons.forEach(button => {
            button.addEventListener('click', function() {
                tabButtons.forEach(btn => btn.classList.remove('active'));
                tabContents.forEach(content => content.classList.remove('active'));
                this.classList.add('active');
                document.getElementById(this.dataset.tab + 'Tab').classList.add('active');
            });
        });

        // --- FORMULÁRIOS COM FETCH ---
        if (loginForm) {
            loginForm.addEventListener('submit', function(e) {
                e.preventDefault();
                const formData = new FormData(loginForm);
                fetch("/login", { method: 'POST', headers: { 'X-Requested-With': 'XMLHttpRequest' }, body: new URLSearchParams(formData) })
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
        if (registerForm) {
            registerForm.addEventListener('submit', function(e) {
                e.preventDefault();
                const formData = new FormData(registerForm);
                fetch("/registrar", { method: 'POST', headers: { 'X-Requested-With': 'XMLHttpRequest' }, body: new URLSearchParams(formData) })
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
    }

    // =================================================================================
    // MÓDULO CENTRAL: INICIALIZAÇÃO GERAL
    // =================================================================================
    
    // Primeiro, inicializamos os componentes visuais da página que não dependem da API
    inicializarLogicaDaPagina();

    // Depois, iniciamos a comunicação com o servidor para ativar os gatilhos inteligentes
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