// =================================================================================
// SYNAPCORTEX - SCRIPT MESTRE DE INTERATIVIDADE
// Versão com tratamento para o Modo de Demonstração
// =================================================================================

document.addEventListener('DOMContentLoaded', function() {

    // -----------------------------------------------------------------------------
    // SEÇÃO 1: LÓGICA DO SITE PRINCIPAL (Página de Vendas / index.html)
    // -----------------------------------------------------------------------------

    // Lógica do Gráfico de Demonstração
    const ctx = document.getElementById('graficoDemonstracao');
    if (ctx) {
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
        setInterval(() => {
            const novoDado = Math.floor(Math.random() * 55) + 40;
            meuGrafico.data.datasets[0].data.shift();
            meuGrafico.data.datasets[0].data.push(novoDado);
            meuGrafico.update();
        }, 2000);
    }

    // Lógica do Modal de Login/Registro
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

    // Lógica do Formulário de Login
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(loginForm);
            const loginErrorMessage = document.getElementById('loginErrorMessage');
            loginErrorMessage.style.display = 'none';

            fetch("/login", { method: 'POST', body: new URLSearchParams(formData) })
                .then(response => response.json().then(data => ({ ok: response.ok, data })))
                .then(({ ok, data }) => {
                    if (ok) {
                        window.location.href = data.redirect_url;
                    } else {
                        loginErrorMessage.textContent = data.message || 'Erro no login.';
                        loginErrorMessage.style.display = 'block';
                    }
                })
                .catch(error => {
                    loginErrorMessage.textContent = 'Erro de comunicação.';
                    loginErrorMessage.style.display = 'block';
                });
        });
    }

    // Lógica do Formulário de Registro
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(registerForm);
            const registerErrorMessage = document.getElementById('registerErrorMessage');
            registerErrorMessage.style.display = 'none';

            fetch("/registrar", { method: 'POST', body: new URLSearchParams(formData) })
                .then(response => response.json().then(data => ({ ok: response.ok, data })))
                .then(({ ok, data }) => {
                    if (ok) {
                        window.location.href = data.redirect_url;
                    } else {
                        registerErrorMessage.textContent = data.message || 'Erro no registro.';
                        registerErrorMessage.style.display = 'block';
                    }
                })
                .catch(error => {
                    registerErrorMessage.textContent = 'Erro de comunicação.';
                    registerErrorMessage.style.display = 'block';
                });
        });
    }
    
    // Lógica do Botão "Test Drive" (Login de Demonstração)
    const demoLoginBtn = document.getElementById('demoLoginBtn');
    if (demoLoginBtn) {
        demoLoginBtn.addEventListener('click', function() {
            const emailField = document.querySelector('#loginTab #modal-email-login');
            const passwordField = document.querySelector('#loginTab #modal-password-login');
            
            if (emailField && passwordField && loginForm) {
                if (modal.style.display !== 'flex') {
                    modal.style.display = 'flex';
                }
                document.querySelector('.tab-button[data-tab="login"]').click();
                
                emailField.value = 'demo@synapcortex.com';
                passwordField.value = 'demo';
                
                loginForm.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
            }
        });
    }


    // -----------------------------------------------------------------------------
    // SEÇÃO 2: LÓGICA DO PAINEL DO CLIENTE (dashboard.html)
    // -----------------------------------------------------------------------------

    // --- CÓDIGO ATUALIZADO PARA TRATAR O MODO DEMO ---
    const configForm = document.getElementById('config-form');
    if (configForm) {
        configForm.addEventListener('submit', (event) => {
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
    // SEÇÃO 3: LÓGICA DO ESPIÃO (Executado no Site do Cliente)
    // -----------------------------------------------------------------------------

    function getApiKeyAndUrl() {
        const scriptTag = document.getElementById('synapcortex-spy-script');
        if (!scriptTag) {
            console.error("SynapCortex: O ID 'synapcortex-spy-script' não foi encontrado.");
            return null;
        }
        const backendUrl = scriptTag.dataset.backendUrl || window.location.origin; 
        const scriptUrl = new URL(scriptTag.src);
        const apiKey = scriptUrl.searchParams.get('key');
        
        if (!apiKey) {
            return null; // Não estamos no site de um cliente
        }
        return { key: apiKey, url: backendUrl };
    }

    let popupMostradoNestaSessao = false;
    function mostrarPopup(motivo, titulo, mensagem) {
        if (popupMostradoNestaSessao) return;
        popupMostradoNestaSessao = true;
        console.log(`SynapCortex: Pop-up acionado! Motivo: ${motivo}`);
        
        const popupDiv = document.createElement('div');
        popupDiv.innerHTML = `
            <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.7); display: flex; justify-content: center; align-items: center; z-index: 9999; font-family: sans-serif;">
                <div style="background-color: #fff; color: #333; padding: 20px 40px; border-radius: 8px; text-align: center; max-width: 400px; position: relative;">
                    <button class="fechar-btn-synapcortex" style="position: absolute; top: 10px; right: 15px; background: none; border: none; font-size: 24px; cursor: pointer; color: #333;">&times;</button>
                    <h2>${titulo}</h2>
                    <p>${mensagem}</p>
                </div>
            </div>
        `;
        document.body.appendChild(popupDiv);
        popupDiv.querySelector('.fechar-btn-synapcortex').addEventListener('click', () => {
            document.body.removeChild(popupDiv);
        });
    }

    function inicializarMotorDeGatilhos(config) {
        console.log("SynapCortex: Ordens recebidas. Inicializando gatilhos...");
        const tituloPadrao = config.popup_titulo || "Não vá embora!";
        const mensagemPadrao = config.popup_mensagem || "Temos uma oferta especial para você.";

        // Gatilho de Abandono (Desktop)
        document.addEventListener('mouseleave', event => {
            if (event.clientY <= 0 && !popupMostradoNestaSessao) {
                mostrarPopup("Abandono Desktop", tituloPadrao, mensagemPadrao);
            }
        });

        // Gatilho "Bem-vindo de Volta"
        if (config.ativar_quarto_bem_vindo) {
            const cookieName = 'synapcortex_visitou';
            if (document.cookie.includes(cookieName)) {
                mostrarPopup("Visitante Recorrente", config.popup_titulo, config.msg_bem_vindo || mensagemPadrao);
            }
            document.cookie = `${cookieName}=true; max-age=31536000; path=/`;
        }
        
        // Gatilho de Inatividade
        if (config.ativar_quarto_interessado) {
            let inactivityTimer;
            const resetTimer = () => {
                clearTimeout(inactivityTimer);
                inactivityTimer = setTimeout(() => {
                    mostrarPopup("Inatividade", config.popup_titulo, config.msg_interessado || mensagemPadrao);
                }, 30000); // 30 segundos
            };
            window.onload = resetTimer;
            document.onmousemove = resetTimer;
            document.onkeydown = resetTimer;
        }
    }


    // -----------------------------------------------------------------------------
    // SEÇÃO 4: BLOCO DE EXECUÇÃO PRINCIPAL
    // -----------------------------------------------------------------------------

    const apiInfo = getApiKeyAndUrl();
    if (apiInfo && apiInfo.key) {
        // Estamos no site de um cliente, inicializar o espião
        fetch(`${apiInfo.url}/api/get-client-config?key=${apiInfo.key}`)
            .then(response => {
                if (!response.ok) throw new Error('Chave de API inválida.');
                return response.json();
            })
            .then(config => {
                if (config) inicializarMotorDeGatilhos(config);
            })
            .catch(error => {
                console.error("SynapCortex: Falha ao obter configurações.", error);
            });
    }
    // Se não encontrou a API Key, significa que o script está no nosso próprio site (index, dashboard)
    // e as lógicas das seções 1 e 2 já foram carregadas.

});