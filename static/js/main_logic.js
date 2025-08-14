// =================================================================================
// SYNAPCORTEX - LÓGICA DO PAINEL E MODAIS (v2.0 - LÓGICA DO PRESENTE SURPRESA)
// =================================================================================

document.addEventListener('DOMContentLoaded', function() {

    // --- LÓGICA DO SELETOR 'PRESENTE SURPRESA' (Passo 1a Concluído) ---
    const abandonoTipoSelect = document.getElementById('abandono-tipo-select');
    if (abandonoTipoSelect) {
        const normalFields = document.getElementById('abandono-normal-fields');
        const presenteFields = document.getElementById('abandono-presente-fields');

        // Função que lê o valor do <select> e alterna a classe .hidden
        function toggleAbandonoFields() {
            if (abandonoTipoSelect.value === 'presente') {
                normalFields.classList.add('hidden');
                presenteFields.classList.remove('hidden');
            } else {
                normalFields.classList.remove('hidden');
                presenteFields.classList.add('hidden');
            }
        }
        
        // Adiciona o evento para responder às mudanças do usuário
        abandonoTipoSelect.addEventListener('change', toggleAbandonoFields);
        
        // O estado inicial já é controlado pelo Jinja2 no HTML, então não precisamos chamar a função aqui.
        // O HTML já carrega com os campos corretos visíveis/escondidos.
    }
    // --- FIM DA LÓGICA DO PRESENTE SURPRESA ---


    // Lógica para ABRIR o Modal de Login/Registro e controlar as abas
    const loginRegisterModal = document.getElementById('loginRegisterModal');
    const openModalBtn = document.getElementById('openLoginRegisterModal');
    const closeBtn = document.querySelector('.modal .close-button');

    if (openModalBtn && loginRegisterModal) {
        openModalBtn.addEventListener('click', () => {
            loginRegisterModal.style.display = 'block';
        });
    }

    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            loginRegisterModal.style.display = 'none';
        });
    }

    window.addEventListener('click', (event) => {
        if (event.target == loginRegisterModal) {
            loginRegisterModal.style.display = 'none';
        }
    });

    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            tabButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            const tab = button.getAttribute('data-tab');
            tabContents.forEach(content => {
                if (content.id === tab + 'Tab') {
                    content.classList.add('active');
                } else {
                    content.classList.remove('active');
                }
            });
        });
    });


    // Lógica para o BOTÃO TEST DRIVE (Login Demo)
    const demoLoginBtn = document.getElementById('demoLoginBtn');
    if (demoLoginBtn) {
        demoLoginBtn.addEventListener('click', function() {
            const loginForm = document.getElementById('loginForm');
            if (loginForm) {
                // Preenche o formulário de login com as credenciais de demonstração
                loginForm.querySelector('input[name="email"]').value = 'demo@synapcortex.com';
                loginForm.querySelector('input[name="password"]').value = 'demo'; // Senha fictícia
                // Envia o formulário
                loginForm.submit();
            }
        });
    }


    // Lógica para o formulário de salvar configurações no DASHBOARD
    const configForm = document.getElementById('config-form');
    if (configForm) {
        configForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(configForm);
            const button = configForm.querySelector('button[type="submit"]');
            const originalButtonText = button.textContent;
            button.textContent = 'Salvando...';
            button.disabled = true;

            fetch(configForm.action, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                // Cria e exibe uma notificação de feedback
                const notification = document.createElement('div');
                notification.className = `notification ${data.status}`; // 'success' ou 'error'
                notification.textContent = data.message;
                document.body.appendChild(notification);
                setTimeout(() => {
                    notification.classList.add('show');
                }, 10);
                setTimeout(() => {
                    notification.classList.remove('show');
                    setTimeout(() => {
                        document.body.removeChild(notification);
                    }, 500);
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


    // Lógica para o botão de copiar no DASHBOARD
    const copiarBtn = document.getElementById('copiar-codigo-btn');
    if (copiarBtn) {
        copiarBtn.addEventListener('click', function() {
            const codigo = document.getElementById('codigo-instalacao');
            codigo.select();
            document.execCommand('copy');
            
            const originalText = copiarBtn.textContent;
            copiarBtn.textContent = 'Copiado!';
            setTimeout(() => {
                copiarBtn.textContent = originalText;
            }, 2000);
        });
    }


    // Lógica para a CENTRAL DE AJUDA INTERATIVA no DASHBOARD
    const helpModal = document.getElementById('helpModal');
    if(helpModal) {
        const platformButtons = document.querySelectorAll('.platform-button');
        const modalTitle = document.getElementById('helpModalTitle');
        const modalContent = document.getElementById('helpModalContent');
        const closeHelpBtn = helpModal.querySelector('.close-button');

        const helpData = {
            shopify: {
                title: 'Instalando na Shopify',
                content: `<ol>
                            <li>No painel da Shopify, vá em <strong>Loja Virtual > Temas</strong>.</li>
                            <li>Clique em <strong>Ações > Editar código</strong>.</li>
                            <li>No menu de arquivos, encontre e abra o arquivo <strong>theme.liquid</strong>.</li>
                            <li>Role até o final do arquivo e cole o seu código da SynapCortex logo antes da tag de fechamento <strong>&lt;/body&gt;</strong>.</li>
                            <li>Clique em <strong>Salvar</strong>. Pronto!</li>
                         </ol>`
            },
            woocommerce: {
                title: 'Instalando no WooCommerce (WordPress)',
                content: `<ol>
                            <li>No painel do WordPress, vá em <strong>Aparência > Editor de arquivos de tema</strong>.</li>
                            <li>No menu direito, encontre e abra o arquivo <strong>Rodapé do Tema (footer.php)</strong>.</li>
                            <li>Role até o final do arquivo e cole o seu código da SynapCortex logo antes da tag de fechamento <strong>&lt;/body&gt;</strong>.</li>
                            <li>Clique em <strong>Atualizar arquivo</strong>. Pronto!</li>
                            <li><strong>Alternativa:</strong> Use um plugin como "Insert Headers and Footers" e cole o código na seção "Scripts in Footer".</li>
                         </ol>`
            },
            nuvemshop: {
                title: 'Instalando na Nuvemshop',
                content: `<ol>
                            <li>No painel da Nuvemshop, acesse <strong>Minha Nuvemshop > Layout</strong>.</li>
                            <li>Clique em <strong>Personalizar seu layout</strong>.</li>
                            <li>Vá em <strong>Configurações avançadas</strong> e role até a parte de <strong>Códigos de rastreamento externos</strong>.</li>
                            <li>Na seção "Códigos de rastreamento externos", cole o seu código da SynapCortex no campo <strong>Rodapé (antes do fechamento da tag &lt;/body&gt;)</strong>.</li>
                            <li>Clique em <strong>Salvar alterações</strong>. Pronto!</li>
                         </ol>`
            },
            universal: {
                title: 'Instalação em Site Próprio',
                content: `<p>Para qualquer site construído com HTML, o processo é o mesmo:</p>
                         <ol>
                            <li>Abra o arquivo HTML principal da sua página (geralmente <strong>index.html</strong> ou um arquivo de layout).</li>
                            <li>Encontre a tag de fechamento <strong>&lt;/body&gt;</strong> no final do arquivo.</li>
                            <li>Cole o seu código da SynapCortex imediatamente antes dessa tag.</li>
                            <li>Se o seu site tem múltiplas páginas, você precisa adicionar este código em todas elas, ou preferencialmente, no arquivo de rodapé global que é incluído em todas as páginas.</li>
                         </ol>`
            }
        };

        platformButtons.forEach(button => {
            button.addEventListener('click', () => {
                const platform = button.dataset.platform;
                modalTitle.textContent = helpData[platform].title;
                modalContent.innerHTML = helpData[platform].content;
                helpModal.style.display = 'block';
            });
        });

        closeHelpBtn.addEventListener('click', () => {
            helpModal.style.display = 'none';
        });

        window.addEventListener('click', (event) => {
            if (event.target == helpModal) {
                helpModal.style.display = 'none';
            }
        });
    }

});