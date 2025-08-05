// =================================================================================
// SYNAPCORTEX - SCRIPT MESTRE DE INTERATIVIDADE
// Versão 1.1 - Final e Estável
// =================================================================================

document.addEventListener('DOMContentLoaded', function() {

    // -----------------------------------------------------------------------------
    // SEÇÃO 1: LÓGICA DA PÁGINA INICIAL (PÁGINA DE VENDAS)
    // -----------------------------------------------------------------------------

    // Lógica do Gráfico de Demonstração
    const ctx = document.getElementById('graficoDemonstracao');
    if (ctx) {
        // ... (código do gráfico que já temos) ...
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
    
    // Lógica do Botão "Login / Cadastre-se" para redirecionar
    const openModalBtn = document.getElementById('openLoginRegisterModal');
    if (openModalBtn) {
        openModalBtn.addEventListener('click', function() {
            window.location.href = '/login';
        });
    }

    // Lógica do Botão "Test Drive" para redirecionar para o login
    const demoLoginBtn = document.getElementById('demoLoginBtn');
    if (demoLoginBtn) {
        demoLoginBtn.addEventListener('click', function() {
            window.location.href = '/login'; // Leva para a página de login onde o usuário pode usar as credenciais 'demo'
        });
    }

    // -----------------------------------------------------------------------------
    // SEÇÃO 2: LÓGICA DO PAINEL DO CLIENTE (DASHBOARD)
    // -----------------------------------------------------------------------------

    const configForm = document.getElementById('config-form');
    if (configForm) {
        configForm.addEventListener('submit', (event) => {
            // A LINHA MAIS IMPORTANTE: Impede o recarregamento antigo
            event.preventDefault(); 
            
            const formData = new FormData(configForm);
            const saveButton = configForm.querySelector('button[type="submit"]');
            
            fetch('/salvar-configuracoes', {
                method: 'POST',
                body: new URLSearchParams(formData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    saveButton.textContent = 'Salvo com Sucesso!';
                    saveButton.style.backgroundColor = '#28a745';
                    setTimeout(() => { window.location.reload(); }, 1500);
                } else if (data.status === 'info') {
                    alert(data.message);
                } else {
                    alert('Ocorreu um erro ao salvar as configurações.');
                }
            })
            .catch(error => {
                console.error('Erro ao salvar:', error);
                alert('Erro de comunicação ao salvar.');
            });
        });
    }

    // -----------------------------------------------------------------------------
    // SEÇÃO 3: LÓGICA DO ESPIÃO (PARA SITES DE CLIENTES)
    // -----------------------------------------------------------------------------
    // (Todo o código do espião, como getApiKey, mostrarPopup, etc. continua aqui)

});