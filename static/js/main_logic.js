// =================================================================================
// SYNAPCORTEX - LÓGICA DO SITE (v1.0 - ARQUIVO DEDICADO)
// =================================================================================

document.addEventListener('DOMContentLoaded', function() {
    
    // Lógica para ABRIR o Modal de Login/Registro e controlar as abas
    const loginRegisterModal = document.getElementById('loginRegisterModal');
    if (loginRegisterModal) {
        const openModalBtn = document.getElementById('openLoginRegisterModal');
        const closeModalBtn = loginRegisterModal.querySelector('.close-button');
        const tabs = loginRegisterModal.querySelectorAll('.tab-button');
        const tabContents = loginRegisterModal.querySelectorAll('.tab-content');

        openModalBtn.addEventListener('click', () => { loginRegisterModal.style.display = 'flex'; });
        closeModalBtn.addEventListener('click', () => { loginRegisterModal.style.display = 'none'; });
        window.addEventListener('click', (e) => { if (e.target == loginRegisterModal) loginRegisterModal.style.display = 'none'; });

        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const target = tab.dataset.tab;
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                tabContents.forEach(c => c.classList.remove('active'));
                document.getElementById(target + 'Tab').classList.add('active');
            });
        });
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
                    saveButton.disabled = false;
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
                    saveButton.disabled = false;
                });
        });
    }

    // Lógica para o botão de copiar no DASHBOARD
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
});