// =================================================================================
// SYNAPCORTEX - LÓGICA DO PAINEL E MODAIS (v6.0 - VERSÃO ESTÁVEL FINAL)
// =================================================================================

document.addEventListener('DOMContentLoaded', function() {

    // --- LÓGICA GERAL DOS MODAIS ---
    function setupModalInteraction(modalElement, openBtn) {
        if (!modalElement || !openBtn) return;

        const closeBtn = modalElement.querySelector('.close-button');

        function openModal() {
            modalElement.style.display = 'block';
            document.body.classList.add('modal-open');
        }

        function closeModal() {
            modalElement.style.display = 'none';
            document.body.classList.remove('modal-open');
        }

        openBtn.addEventListener('click', openModal);
        if (closeBtn) closeBtn.addEventListener('click', closeModal);
        modalElement.addEventListener('click', function(event) {
            if (event.target === modalElement) closeModal();
        });
    }

    setupModalInteraction(document.getElementById('loginRegisterModal'), document.getElementById('openLoginRegisterModal'));

    // --- LÓGICA DA CENTRAL DE AJUDA ---
    const helpModal = document.getElementById('helpModal');
    if (helpModal) {
        const platformButtons = document.querySelectorAll('.platform-button');
        const modalTitle = document.getElementById('helpModalTitle');
        const modalContent = document.getElementById('helpModalContent');
        const closeHelpBtn = helpModal.querySelector('.close-button');

        const helpData = {
            shopify: { title: 'Instalando na Shopify', content: `<ol><li>No painel da Shopify, vá em <strong>Loja Virtual > Temas</strong>.</li><li>Clique em <strong>Ações > Editar código</strong>.</li><li>No menu de arquivos, encontre e abra o arquivo <strong>theme.liquid</strong>.</li><li>Role até o final do arquivo e cole o seu código da SynapCortex logo antes da tag de fechamento <strong>&lt;/body&gt;</strong>.</li><li>Clique em <strong>Salvar</strong>. Pronto!</li></ol>` },
            woocommerce: { title: 'Instalando no WooCommerce (WordPress)', content: `<ol><li>No painel do WordPress, vá em <strong>Aparência > Editor de arquivos de tema</strong>.</li><li>No menu direito, encontre e abra o arquivo <strong>Rodapé do Tema (footer.php)</strong>.</li><li>Role até o final do arquivo e cole o seu código da SynapCortex logo antes da tag de fechamento <strong>&lt;/body&gt;</strong>.</li><li>Clique em <strong>Atualizar arquivo</strong>. Pronto!</li></ol>` },
            nuvemshop: { title: 'Instalando na Nuvemshop', content: `<ol><li>No painel da Nuvemshop, acesse <strong>Minha Nuvemshop > Layout</strong>.</li><li>Clique em <strong>Personalizar seu layout</strong>.</li><li>Vá em <strong>Configurações avançadas</strong> e role até a parte de <strong>Códigos de rastreamento externos</strong>.</li><li>Na seção "Códigos de rastreamento externos", cole o seu código da SynapCortex no campo <strong>Rodapé</strong>.</li><li>Clique em <strong>Salvar alterações</strong>. Pronto!</li></ol>` },
            universal: { title: 'Instalação em Site Próprio', content: `<p>Para qualquer site construído com HTML, o processo é o mesmo:</p><ol><li>Abra o arquivo HTML principal da sua página (geralmente <strong>index.html</strong> ou um arquivo de layout).</li><li>Encontre a tag de fechamento <strong>&lt;/body&gt;</strong> no final do arquivo.</li><li>Cole o seu código da SynapCortex imediatamente antes dessa tag.</li></ol>` }
        };

        platformButtons.forEach(button => {
            button.addEventListener('click', () => {
                const platform = button.dataset.platform;
                modalTitle.textContent = helpData[platform].title;
                modalContent.innerHTML = helpData[platform].content;
                helpModal.style.display = 'block';
                document.body.classList.add('modal-open');
            });
        });

        if (closeHelpBtn) closeHelpBtn.addEventListener('click', () => { helpModal.style.display = 'none'; document.body.classList.remove('modal-open'); });
        helpModal.addEventListener('click', (event) => { if (event.target === helpModal) { helpModal.style.display = 'none'; document.body.classList.remove('modal-open'); } });
    }

    // --- LÓGICA DO PAINEL ---
    const abandonoTipoSelect = document.getElementById('abandono-tipo-select');
    if (abandonoTipoSelect) {
        const normalFields = document.getElementById('abandono-normal-fields');
        const presenteFields = document.getElementById('abandono-presente-fields');
        function toggleAbandonoFields() {
            if (abandonoTipoSelect.value === 'presente') {
                normalFields.classList.add('hidden');
                presenteFields.classList.remove('hidden');
            } else {
                normalFields.classList.remove('hidden');
                presenteFields.classList.add('hidden');
            }
        }
        toggleAbandonoFields();
        abandonoTipoSelect.addEventListener('change', toggleAbandonoFields);
    }

    const configForm = document.getElementById('config-form');
    if (configForm) {
        configForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(configForm);
            const button = configForm.querySelector('button[type="submit"]');
            const originalButtonText = button.textContent;
            button.textContent = 'Salvando...';
            button.disabled = true;

            fetch(configForm.action, { method: 'POST', body: formData })
            .then(response => response.json())
            .then(data => {
                const notification = document.createElement('div');
                notification.className = `notification ${data.status}`;
                notification.textContent = data.message;
                document.body.appendChild(notification);
                setTimeout(() => { notification.classList.add('show'); }, 10);
                setTimeout(() => {
                    notification.classList.remove('show');
                    setTimeout(() => { document.body.removeChild(notification); }, 500);
                }, 3000);
                button.textContent = originalButtonText;
                button.disabled = false;
            })
            .catch(error => {
                console.error('Erro:', error);
                button.textContent = originalButtonText;
                button.disabled = false;
            });
        });
    }

    const copiarBtn = document.getElementById('copiar-codigo-btn');
    if (copiarBtn) {
        copiarBtn.addEventListener('click', function() {
            const codigo = document.getElementById('codigo-instalacao');
            codigo.select();
            document.execCommand('copy');
            const originalText = copiarBtn.textContent;
            copiarBtn.textContent = 'Copiado!';
            setTimeout(() => { copiarBtn.textContent = originalText; }, 2000);
        });
    }
});