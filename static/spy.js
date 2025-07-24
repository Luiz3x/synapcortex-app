document.addEventListener('DOMContentLoaded', function() {

    // --- Funções para Manipulação de Cookies ---
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

    // --- Lógica do Pop-up de Saída ---
    let popupMostrado = false;
    function mostrarPopup() {
        if (popupMostrado) return;
        popupMostrado = true;
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

    document.addEventListener('mouseleave', function(event) {
        if (event.clientY <= 0) {
            mostrarPopup();
        }
    });

    const fecharPopupBtn = document.getElementById('fechar-popup');
    if (fecharPopupBtn) {
        fecharPopupBtn.addEventListener('click', function() {
            document.getElementById('popup-espiao').style.display = 'none';
        });
    }

    // --- Lógica do Modal de Login/Cadastro ---
    const modal = document.getElementById('loginRegisterModal');
    const openModalBtn = document.getElementById('openLoginRegisterModal');
    const closeButton = document.querySelector('.close-button');
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

    // Lógica de envio do formulário de Login via Fetch
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

    // Lógica de envio do formulário de Registro via Fetch
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

    // --- Lógica de Gerenciamento de Visitante (Cookies) ---
    const cookieName = 'synapcortex_visitou';
    if (getCookie(cookieName)) {
        // É um visitante recorrente! Mostra o pop-up.
        document.getElementById('popup-bemvindo').style.display = 'flex';
    } else {
        console.log("Olá! (Primeira Visita)");
        setCookie(cookieName, 'true', 365);
    }
});       
    // "Escuta" o clique no botão de fechar do pop-up de Bem-vindo
const fecharBemvindoBtn = document.getElementById('fechar-bemvindo');
if (fecharBemvindoBtn) {
    fecharBemvindoBtn.addEventListener('click', function() {
        document.getElementById('popup-bemvindo').style.display = 'none';
    });
} 
// --- Lógica do Gráfico de Demonstração ---

// Função para iniciar o gráfico
function iniciarGraficoDemo() {
    const ctx = document.getElementById('graficoDemonstracao');
    // Se o elemento do gráfico não existir nesta página, não faz nada.
    if (!ctx) {
        return;
    }

    const labels = ['-50s', '-40s', '-30s', '-20s', '-10s', 'Agora'];
    const data = {
        labels: labels,
        datasets: [{
            label: 'Clientes Recuperados',
            backgroundColor: 'rgba(0, 204, 255, 0.2)', // Cor do preenchimento (ciano com transparência)
            borderColor: 'rgba(0, 204, 255, 1)', // Cor da linha (ciano sólido)
            data: [65, 59, 80, 81, 56, 55], // Dados iniciais "fake"
            fill: true,
            tension: 0.4 // Deixa a linha com curvas suaves
        }]
    };

    const config = {
        type: 'line', // Tipo do gráfico: linha
        data: data,
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false // Esconde a legenda "Clientes Recuperados"
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { color: '#bbbbbb' }, // Cor dos números no eixo Y
                    grid: { color: 'rgba(255, 255, 255, 0.1)' } // Cor das linhas de grade
                },
                x: {
                    ticks: { color: '#bbbbbb' }, // Cor dos textos no eixo X
                    grid: { display: false } // Esconde a grade do eixo X
                }
            }
        }
    };

    const meuGrafico = new Chart(ctx, config);

    // Animação para fazer o gráfico parecer "vivo"
    setInterval(function() {
        // Gera um novo número aleatório
        const novoDado = Math.floor(Math.random() * (95 - 40 + 1) + 40);
        
        // Remove o dado mais antigo do gráfico
        meuGrafico.data.datasets[0].data.shift();
        // Adiciona o novo dado no final
        meuGrafico.data.datasets[0].data.push(novoDado);
        
        // Atualiza o gráfico na tela com a animação
        meuGrafico.update();
    }, 2000); // Atualiza a cada 2 segundos (2000 ms)
}

// Garante que o código do gráfico só rode depois que a página carregou
document.addEventListener('DOMContentLoaded', iniciarGraficoDemo);