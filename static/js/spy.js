// =================================================================================
// SYNAPCORTEX - SCRIPT MESTRE DE INTERATIVIDADE
// Versão com Gatilho de Abandono Robusto (Desktop & Mobile)
// =================================================================================

document.addEventListener('DOMContentLoaded', function() {

    // -----------------------------------------------------------------------------
    // SEÇÃO 1: LÓGICA DO SITE PRINCIPAL (Página de Vendas / index.html)
    // -----------------------------------------------------------------------------

    // Lógica do Gráfico de Demonstração
    const ctx = document.getElementById('graficoDemonstracao');
    if (ctx) {
        // ... (código do gráfico que já temos) ...
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
        const config = { type: 'line', data: data, options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { color: '#bbbbbb' }, grid: { color: 'rgba(255, 255, 255, 0.1)' } }, x: { ticks: { color: '#bbbbbb' }, grid: { display: false } } } } };
        const meuGrafico = new Chart(ctx, config);
        setInterval(() => {
            const novoDado = Math.floor(Math.random() * 55) + 40;
            meuGrafico.data.datasets[0].data.shift();
            meuGrafico.data.datasets[0].data.push(novoDado);
            meuGrafico.update();
        }, 2000);
    }

    // Lógica do Modal de Login/Registro e Forms
    // ... (todo o código dos formulários de login, registro e botão demo que já temos) ...
    const modal = document.getElementById('loginRegisterModal');
    const openModalBtn = document.getElementById('openLoginRegisterModal');
    const closeButton = document.querySelector('.modal .close-button');
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    if (openModalBtn) { openModalBtn.onclick = () => { modal.style.display = 'flex'; }; }
    if (closeButton) { closeButton.onclick = () => { modal.style.display = 'none'; }; }
    window.onclick = event => { if (event.target == modal) { modal.style.display = 'none'; } };
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            this.classList.add('active');
            document.getElementById(this.dataset.tab + 'Tab').classList.add('active');
        });
    });
    const loginForm = document.getElementById('loginForm');
    if (loginForm) { loginForm.addEventListener('submit', function(e) { /* ...código fetch login... */ }); }
    const registerForm = document.getElementById('registerForm');
    if (registerForm) { registerForm.addEventListener('submit', function(e) { /* ...código fetch registro... */ }); }
    const demoLoginBtn = document.getElementById('demoLoginBtn');
    if (demoLoginBtn) { demoLoginBtn.addEventListener('click', function() { /* ...código login demo... */ }); }

    // -----------------------------------------------------------------------------
    // SEÇÃO 2: LÓGICA DO PAINEL DO CLIENTE (dashboard.html)
    // -----------------------------------------------------------------------------
    
    const configForm = document.getElementById('config-form');
    if (configForm) {
        // ... (código do formulário de salvar configurações que já temos, com tratamento do modo demo) ...
        configForm.addEventListener('submit', (event) => {
            event.preventDefault();
            const formData = new FormData(configForm);
            fetch('/salvar-configuracoes', { method: 'POST', body: new URLSearchParams(formData) })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') { /* ...código de sucesso... */ } 
                else if (data.status === 'info') { alert(data.message); } 
                else { alert('Ocorreu um erro.'); }
            })
            .catch(error => { alert('Erro de comunicação.'); });
        });
    }

    // -----------------------------------------------------------------------------
    // SEÇÃO 3: LÓGICA DO ESPIÃO (Executado no Site do Cliente)
    // -----------------------------------------------------------------------------

    function getApiKeyAndUrl() {
        const scriptTag = document.getElementById('synapcortex-spy-script');
        if (!scriptTag) return null;
        const backendUrl = scriptTag.dataset.backendUrl || window.location.origin;
        const scriptUrl = new URL(scriptTag.src);
        const apiKey = scriptUrl.searchParams.get('key');
        if (!apiKey) return null;
        return { key: apiKey, url: backendUrl };
    }

    let popupMostradoNestaSessao = false;
    function mostrarPopup(motivo, titulo, mensagem) {
        if (popupMostradoNestaSessao) return;
        popupMostradoNestaSessao = true;
        console.log(`SynapCortex: Pop-up acionado! Motivo: ${motivo}`);
        const popupDiv = document.createElement('div');
        popupDiv.innerHTML = `<div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.7); display: flex; justify-content: center; align-items: center; z-index: 9999; font-family: sans-serif;"><div style="background-color: #fff; color: #333; padding: 20px 40px; border-radius: 8px; text-align: center; max-width: 400px; position: relative;"><button class="fechar-btn-synapcortex" style="position: absolute; top: 10px; right: 15px; background: none; border: none; font-size: 24px; cursor: pointer; color: #333;">&times;</button><h2>${titulo}</h2><p>${mensagem}</p></div></div>`;
        document.body.appendChild(popupDiv);
        popupDiv.querySelector('.fechar-btn-synapcortex').addEventListener('click', () => { document.body.removeChild(popupDiv); });
    }

    // ========== CÓDIGO ATUALIZADO E ROBUSTO ==========
    function inicializarMotorDeGatilhos(config) {
        console.log("SynapCortex: Ordens recebidas. Inicializando gatilhos...");

        const tituloPadrao = config.popup_titulo || "Espere, não vá ainda!";
        const mensagemPadrao = config.popup_mensagem || "Temos uma oferta especial para você.";

        // --- GATILHO DE ABANDONO (LÓGICA DUPLA: DESKTOP E MOBILE) ---
        const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);

        if (isMobile) {
            // ESTRATÉGIA MOBILE: Detectar a troca de abas ou de apps
            console.log("SynapCortex: Modo mobile ativado.");
            document.addEventListener('visibilitychange', () => {
                if (document.visibilityState === 'hidden' && !popupMostradoNestaSessao) {
                    mostrarPopup("Abandono Mobile (Troca de Aba)", tituloPadrao, mensagemPadrao);
                }
            });
        } else {
            // ESTRATÉGIA DESKTOP: Detectar a saída do mouse pelo topo da página
            console.log("SynapCortex: Modo desktop ativado.");
            document.addEventListener('mouseleave', event => {
                if (event.clientY <= 0 && !popupMostradoNestaSessao) {
                    mostrarPopup("Abandono Desktop (Saída do Mouse)", tituloPadrao, mensagemPadrao);
                }
            });
        }

        // --- OUTROS GATILHOS ("QUARTOS") ---
        if (config.ativar_quarto_bem_vindo) { /* ...lógica... */ }
        if (config.ativar_quarto_interessado) { /* ...lógica... */ }
    }
    // ===============================================

    // -----------------------------------------------------------------------------
    // SEÇÃO 4: BLOCO DE EXECUÇÃO PRINCIPAL
    // -----------------------------------------------------------------------------

    const apiInfo = getApiKeyAndUrl();
    if (apiInfo && apiInfo.key) {
        fetch(`${apiInfo.url}/api/get-client-config?key=${apiInfo.key}`)
            .then(response => response.json())
            .then(config => { if (config) inicializarMotorDeGatilhos(config); })
            .catch(error => { console.error("SynapCortex: Falha ao obter configurações.", error); });
    }
});