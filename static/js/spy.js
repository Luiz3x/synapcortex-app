// =================================================================================
// SYNAPCORTEX - SCRIPT MESTRE (v3.2 - CORREÇÃO LÓGICA DO SITE)
// =================================================================================

document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('synapcortex-spy-script')) {
        if (typeof synapseAgent !== 'undefined' && synapseAgent.init()) {
            runSynapseAgent();
            return;
        }
    }
    runSynapCortexSiteLogic();
});

// PARTE 1: O AGENTE ESPIÃO (SÓ RODA NO SITE DO CLIENTE)
const synapseAgent = {
    apiKey: null, backendUrl: null, visitorId: null,
    init: function() {
        const scriptTag = document.getElementById('synapcortex-spy-script');
        if (!scriptTag) return false;
        try {
            const key = new URL(scriptTag.src).searchParams.get('key');
            if (!key) return false;
            this.apiKey = key;
        } catch(e) { return false; }
        this.backendUrl = scriptTag.dataset.backendUrl || 'https://synapcortex-app.onrender.com';
        let storedVisitorId = localStorage.getItem('synapcortex_visitor_id');
        if (!storedVisitorId) {
            storedVisitorId = Date.now() + '-' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('synapcortex_visitor_id', storedVisitorId);
        }
        this.visitorId = storedVisitorId;
        return true;
    },
    trackEvent: function(eventName, eventData = {}) {
        if (!this.apiKey) return;
        const payload = { apiKey: this.apiKey, visitorId: this.visitorId, eventName, eventData };
        try {
            navigator.sendBeacon(`${this.backendUrl}/api/track`, JSON.stringify(payload));
        } catch (e) {
            fetch(`${this.backendUrl}/api/track`, { method: 'POST', body: JSON.stringify(payload), headers: { 'Content-Type': 'application/json' }, keepalive: true }).catch(console.error);
        }
    }
};

function runSynapseAgent() {
    // Lógica do espião que roda no site do cliente
    synapseAgent.trackEvent('pagina_visitada', { url: window.location.pathname, title: document.title });
    // ... (restante da lógica do espião, como pop-ups)
}

// PARTE 2: LÓGICA DO NOSSO SITE (PÁGINA INICIAL E DASHBOARD)
function runSynapCortexSiteLogic() {
    // Lógica para o Modal de Login/Registro na index.html
    const loginRegisterModal = document.getElementById('loginRegisterModal');
    if (loginRegisterModal) {
        const openModalBtn = document.getElementById('openLoginRegisterModal');
        const closeModalBtn = loginRegisterModal.querySelector('.close-button');
        const loginForm = document.getElementById('loginForm');
        const registerForm = document.getElementById('registerForm');
        const demoLoginBtn = document.getElementById('demoLoginBtn');

        openModalBtn.addEventListener('click', () => { loginRegisterModal.style.display = 'flex'; });
        closeModalBtn.addEventListener('click', () => { loginRegisterModal.style.display = 'none'; });
        window.addEventListener('click', (e) => { if (e.target == loginRegisterModal) loginRegisterModal.style.display = 'none'; });

        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            this.submit(); // Envia o formulário da maneira tradicional
        });
        registerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            this.submit(); // Envia o formulário da maneira tradicional
        });

        if (demoLoginBtn) {
            demoLoginBtn.addEventListener('click', function() {
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = '/login';
                const emailInput = document.createElement('input');
                emailInput.type = 'hidden';
                emailInput.name = 'email';
                emailInput.value = 'demo@synapcortex.com';
                form.appendChild(emailInput);
                const passInput = document.createElement('input');
                passInput.type = 'hidden';
                passInput.name = 'password';
                passInput.value = 'demo';
                form.appendChild(passInput);
                document.body.appendChild(form);
                form.submit();
            });
        }
    }

    // Lógica para o botão de copiar no dashboard.html
    const copiarBtn = document.getElementById('copiar-codigo-btn');
    if (copiarBtn) {
        copiarBtn.addEventListener('click', () => {
            const codigoTextarea = document.getElementById('codigo-instalacao');
            navigator.clipboard.writeText(codigoTextarea.value).then(() => {
                copiarBtn.textContent = 'Copiado!';
                setTimeout(() => { copiarBtn.textContent = 'Copiar Código'; }, 2000);
            }, () => {
                copiarBtn.textContent = 'Erro ao copiar';
            });
        });
    }
    
    // Lógica para o form de config no dashboard.html
    const configForm = document.getElementById('config-form');
    if (configForm) {
        configForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(configForm);
            const saveButton = configForm.querySelector('button[type="submit"]');
            saveButton.textContent = 'Salvando...';
            fetch('/salvar-configuracoes', { method: 'POST', body: new URLSearchParams(formData) })
                .then(res => res.json())
                .then(data => {
                    if (data.status === 'success') {
                        saveButton.textContent = 'Salvo com Sucesso!';
                        saveButton.style.backgroundColor = 'var(--success-green)';
                        setTimeout(() => window.location.reload(), 1500);
                    } else {
                         saveButton.textContent = 'Erro ao Salvar';
                         alert(data.message || 'Ocorreu um erro.');
                    }
                }).catch(() => {
                    saveButton.textContent = 'Erro de comunicação';
                });
        });
    }
}