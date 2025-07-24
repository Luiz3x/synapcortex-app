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