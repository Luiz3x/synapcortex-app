// =================================================================================
// SYNAPCORTEX - LÓGICA DO PAINEL E MODAIS (v6.2 - VERSÃO ESTÁVEL CORRIGIDA)
// =================================================================================

document.addEventListener('DOMContentLoaded', () => {

    // --- LÓGICA 1: SALVAR CONFIGURAÇÕES COM FETCH ---
    const configForm = document.getElementById('config-form');
    if (configForm) {
        configForm.addEventListener('submit', (event) => {
            event.preventDefault();

            const formData = new FormData(configForm);
            const saveButton = configForm.querySelector('button[type="submit"]');
            const originalButtonText = saveButton.textContent;

            saveButton.textContent = 'Salvando...';
            saveButton.disabled = true;

            fetch('/salvar-configuracoes', {
                method: 'POST',
                body: formData 
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Resposta do servidor não foi OK');
                }
                return response.json();
            })
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

                saveButton.textContent = originalButtonText;
                saveButton.disabled = false;
            })
            .catch(error => {
                console.error('Erro de comunicação:', error);
                alert('Não foi possível conectar ao servidor. Verifique sua conexão.');
                saveButton.textContent = originalButtonText;
                saveButton.disabled = false;
            });
        });
    }

    // --- LÓGICA 2: MODAL DA CENTRAL DE AJUDA ---
    const helpModal = document.getElementById('helpModal');
    if (helpModal) {
        const helpModalTitle = document.getElementById('helpModalTitle');
        const helpModalContent = document.getElementById('helpModalContent');
        const closeModalBtn = helpModal.querySelector('.close-button');

        const helpData = {
            shopify: { title: 'Instalando na Shopify', content: `<ol><li>Acesse "Loja Virtual" > "Temas".</li><li>Clique em (...) e escolha "Editar código".</li><li>Em "Layout", clique no arquivo 'theme.liquid'.</li><li>Cole o seu código acima da tag <code>&lt;/body&gt;</code>.</li><li>Salve. Pronto!</li></ol>` },
            woocommerce: { title: 'Instalando no WooCommerce (WordPress)', content: `<ol><li>No seu painel WordPress, vá em "Aparência" > "Editor de Arquivos de Tema".</li><li>Na lista à direita, encontre e clique em "Rodapé do Tema (footer.php)".</li><li>Cole o seu código acima da tag <code>&lt;/body&gt;</code>.</li><li>Clique em "Atualizar arquivo". Pronto!</li></ol>` },
            nuvemshop: { title: 'Instalando na Nuvemshop', content: `<ol><li>No painel da sua Nuvemshop, clique em "Configurações".</li><li>Procure por "Códigos externos".</li><li>Role até "Códigos de rastreamento".</li><li>Cole o seu código na caixa "No corpo do site".</li><li>Clique em "Salvar alterações". Pronto!</li></ol>` },
            universal: { title: 'Instalação Universal (Qualquer Site HTML)', content: `<ol><li>Encontre seu arquivo HTML principal.</li><li>Localize a tag <code>&lt;/body&gt;</code>.</li><li>Cole o seu código acima da tag.</li><li>Salve e publique.</li></ol>` }
        };

        document.querySelectorAll('.platform-button').forEach(button => {
            button.addEventListener('click', function() {
                const platform = this.dataset.platform;
                if (helpData[platform]) {
                    helpModalTitle.textContent = helpData[platform].title;
                    helpModalContent.innerHTML = helpData[platform].content;
                }
                helpModal.style.display = 'block';
                document.body.classList.add('modal-open');
            });
        });

        const closeModal = () => {
            helpModal.style.display = 'none';
            document.body.classList.remove('modal-open');
        };

        closeModalBtn.addEventListener('click', closeModal);
        window.addEventListener('click', (event) => {
            if (event.target == helpModal) {
                closeModal();
            }
        });
    }

    // --- LÓGICA 3: MOSTRAR/ESCONDER CAMPOS DO "PRESENTE SURPRESA" ---
    const tipoAbandonoSelect = document.getElementById('abandono-tipo-select');
    if (tipoAbandonoSelect) {
        const presenteFields = document.getElementById('abandono-presente-fields');
        const normalFields = document.getElementById('abandono-normal-fields');

        const toggleFields = () => {
            if (tipoAbandonoSelect.value === 'presente') {
                presenteFields.classList.remove('hidden');
                normalFields.classList.add('hidden');
            } else {
                presenteFields.classList.add('hidden');
                normalFields.classList.remove('hidden');
            }
        };
        tipoAbandonoSelect.addEventListener('change', toggleFields);
        toggleFields();
    }

    // --- LÓGICA 4: BOTÃO DE COPIAR CÓDIGO ---
    const copiarBtn = document.getElementById('copiar-codigo-btn');
    if (copiarBtn) {
        copiarBtn.addEventListener('click', function() {
            const codigoTextarea = document.getElementById('codigo-instalacao');
            navigator.clipboard.writeText(codigoTextarea.value).then(() => {
                copiarBtn.textContent = 'Copiado!';
                setTimeout(() => {
                    copiarBtn.textContent = 'Copiar Código';
                }, 2000);
            }).catch(err => {
                console.error('Falha ao copiar: ', err);
            });
        });
    }
});