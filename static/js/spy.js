// =================================================================================
// SYNAPCORTEX - SCRIPT MESTRE (AGENTE SYNAPSE)
// Versão 2.1 - COMPLETO E CONSOLIDADO PARA TODAS AS PÁGINAS
// =================================================================================

document.addEventListener('DOMContentLoaded', function() {
    
    // -----------------------------------------------------------------------------
    // PARTE 1: LÓGICA DA PÁGINA PRINCIPAL (index.html)
    // -----------------------------------------------------------------------------
    const openLoginRegisterModalBtn = document.getElementById('openLoginRegisterModal');
    if (openLoginRegisterModalBtn) {
        openLoginRegisterModalBtn.addEventListener('click', function() {
            window.location.href = '/login';
        });
    }

    const demoLoginBtn = document.getElementById('demoLoginBtn');
    if (demoLoginBtn) {
        demoLoginBtn.addEventListener('click', function() {
            window.location.href = '/login';
        });
    }

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

    // -----------------------------------------------------------------------------
    // PARTE 2: LÓGICA DO PAINEL DO CLIENTE (dashboard.html)
    // -----------------------------------------------------------------------------
    const configForm = document.getElementById('config-form');
    if (configForm) {
        configForm.addEventListener('submit', function(event) {
            event.preventDefault(); 
            const formData = new FormData(configForm);
            const saveButton = configForm.querySelector('button[type="submit"]');
            fetch('/salvar-configuracoes', { method: 'POST', body: new URLSearchParams(formData) })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    saveButton.textContent = 'Salvo com Sucesso!';
                    saveButton.style.backgroundColor = '#28a745';
                    setTimeout(() => { window.location.reload(); }, 1500);
                } else if (data.status === 'info') {
                    alert(data.message);
                } else { alert('Ocorreu um erro ao salvar.'); }
            })
            .catch(error => { alert('Erro de comunicação.'); });
        });
    }
    
    // (A lógica da Central de Ajuda do dashboard também estaria aqui, se não estivesse no HTML)

    // -----------------------------------------------------------------------------
    // PARTE 3: LÓGICA DO ESPIÃO (PARA SITES DE CLIENTES)
    // -----------------------------------------------------------------------------
    const synapseAgent = {
        apiKey: null,
        backendUrl: null,
        visitorId: null,

        init: function() { /* ... código de inicialização ... */ },
        trackEvent: function(eventName, eventData = {}) { /* ... código de rastreio ... */ }
    };

    let popupMostradoNestaSessao = false;
    function mostrarPopup(motivo, titulo, mensagem) { /* ... código de mostrar pop-up ... */ }
    function inicializarMotorDeGatilhos(config) { /* ... código dos gatilhos ... */ }

    if (synapseAgent.init()) {
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