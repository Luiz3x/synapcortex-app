// =================================================================================
// SYNAPCORTEX - SCRIPT MESTRE (v3.3 - VERSÃO SIMPLIFICADA E FINAL)
// =================================================================================

document.addEventListener('DOMContentLoaded', function() {
    // Verifica se o script do espião está na página para decidir qual lógica rodar
    if (document.getElementById('synapcortex-spy-script')) {
        // Lógica do espião (site do cliente)
        if (typeof synapseAgent !== 'undefined' && synapseAgent.init()) {
            runSynapseAgent();
            return;
        }
    }
    // Lógica do nosso site (synapcortex-app.onrender.com)
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
            // Usa sendBeacon para envios assíncronos e confiáveis (bom para saídas de página)
            navigator.sendBeacon(`${this.backendUrl}/api/track`, JSON.stringify(payload));
        } catch (e) {
            // Fallback para navegadores mais antigos ou casos onde sendBeacon não é suportado
            fetch(`${this.backendUrl}/api/track`, { method: 'POST', body: JSON.stringify(payload), headers: { 'Content-Type': 'application/json' }, keepalive: true }).catch(console.error);
        }
    }
};

function runSynapseAgent() {
    synapseAgent.trackEvent('pagina_visitada', { url: window.location.pathname, title: document.title });
    // Futuramente, a lógica de inicializar pop-ups e outros gatilhos com base na config do cliente virá aqui
}

// PARTE 2: LÓGICA DO NOSSO SITE (PÁGINA INICIAL E DASHBOARD)
function runSynapCortexSiteLogic() {
    
    // Lógica para ABRIR o Modal de Login/Registro
    const loginRegisterModal = document.getElementById('loginRegisterModal');
    if (loginRegisterModal) {
        const openModalBtn = document.getElementById('openLoginRegisterModal');
        const closeModalBtn = loginRegisterModal.querySelector('.close-button');
        openModalBtn.addEventListener('click', () => { loginRegisterModal.style.display = 'flex'; });
        closeModalBtn.addEventListener('click', () => { loginRegisterModal.style.display = 'none'; });
        window.addEventListener('click', (e) => { if (e.target == loginRegisterModal) loginRegisterModal.style.display = 'none'; });
    }
    
    // Lógica para o BOTÃO TEST DRIVE
    const demoLoginBtn = document.getElementById('demoLoginBtn');
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

    // Lógica para o formulário de salvar configurações no DASHBOARD
    const configForm = document.getElementById('config-form');
    if (configForm) {
        configForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(configForm);
            const saveButton = configForm.querySelector('button[type="submit"]');
            saveButton.textContent = 'Salvando...';
            saveButton.disabled = true;

            fetch('/salvar-configuracoes', { method: 'POST', body: new URLSearchParams(formData) })
                .then(res => res.json())
                .then(data => {
                    if (data.status === 'success') {
                        saveButton.textContent = 'Salvo com Sucesso!';
                        saveButton.style.backgroundColor = 'var(--success-green)';
                        setTimeout(() => window.location.reload(), 1500);
                    } else {
                         saveButton.textContent = 'Erro ao Salvar';
                         saveButton.disabled = false;
                         alert(data.message || 'Ocorreu um erro.');
                    }
                }).catch(() => {
                    saveButton.textContent = 'Erro de comunicação';
                    saveButton.disabled = false;
                });
        });
    }

    // Lógica para o botão de copiar no DASHBOARD (versão moderna)
    const copiarBtn = document.getElementById('copiar-codigo-btn');
    if (copiarBtn) {
        const codigoTextarea = document.getElementById('codigo-instalacao');
        copiarBtn.addEventListener('click', () => {
            navigator.clipboard.writeText(codigoTextarea.value).then(() => {
                copiarBtn.textContent = 'Copiado!';
                setTimeout(() => { copiarBtn.textContent = 'Copiar Código'; }, 2000);
            }, () => {
                copiarBtn.textContent = 'Erro ao copiar';
            });
        });
    }

    // Lógica para o modal de ajuda no DASHBOARD
    const helpModal = document.getElementById('helpModal');
    if(helpModal) {
        const helpModalTitle = document.getElementById('helpModalTitle');
        const helpModalContent = document.getElementById('helpModalContent');
        const closeModalBtn = helpModal.querySelector('.close-button');
        document.querySelectorAll('.platform-button').forEach(button => {
            button.addEventListener('click', function() {
                // ... (toda a lógica para preencher e mostrar o modal de ajuda) ...
            });
        });
        closeModalBtn.onclick = () => { helpModal.style.display = 'none'; };
        window.onclick = event => { if (event.target == helpModal) { helpModal.style.display = 'none'; } };
    }
}