// =================================================================================
// SYNAPCORTEX - LÓGICA DO SITE (v1.1 - CORREÇÃO DA CENTRAL DE AJUDA)
// =================================================================================

document.addEventListener('DOMContentLoaded', function() {
    
    // Lógica para ABRIR o Modal de Login/Registro e controlar as abas
    const loginRegisterModal = document.getElementById('loginRegisterModal');
    if (loginRegisterModal) {
        // ... (toda a lógica do modal de login que já funciona, não precisa mexer)
    }
    
    // Lógica para o BOTÃO TEST DRIVE
    const demoLoginBtn = document.getElementById('demoLoginBtn');
    if (demoLoginBtn) {
        // ... (toda a lógica do test drive que já funciona, não precisa mexer)
    }

    // Lógica para o formulário de salvar configurações no DASHBOARD
    const configForm = document.getElementById('config-form');
    if (configForm) {
        // ... (toda a lógica de salvar que já funciona, não precisa mexer)
    }

    // Lógica para o botão de copiar no DASHBOARD
    const copiarBtn = document.getElementById('copiar-codigo-btn');
    if (copiarBtn) {
        // ... (toda a lógica de copiar que já funciona, não precisa mexer)
    }

    // --- CORREÇÃO DA CENTRAL DE AJUDA INTERATIVA ---
    const helpModal = document.getElementById('helpModal');
    if(helpModal) {
        const helpModalTitle = document.getElementById('helpModalTitle');
        const helpModalContent = document.getElementById('helpModalContent');
        const closeModalBtn = helpModal.querySelector('.close-button');

        document.querySelectorAll('.platform-button').forEach(button => {
            button.addEventListener('click', function() {
                const platform = this.dataset.platform;
                let title = 'Guia de Instalação';
                let content = '<p>As instruções para esta plataforma estarão disponíveis em breve!</p>';
                
                if (platform === 'shopify') {
                    title = 'Instalando na Shopify';
                    content = `<ol style="text-align: left; padding-left: 20px;">
                                 <li>Acesse "Loja Virtual" > "Temas".</li>
                                 <li>Clique em "Personalizar", depois nos 3 pontinhos (...) e escolha "Editar código".</li>
                                 <li>Na lista de arquivos à esquerda, em "Layout", clique no arquivo <strong>theme.liquid</strong>.</li>
                                 <li>Role até o final e cole o seu código da SynapCortex logo acima da tag <code>&lt;/body&gt;</code>.</li>
                                 <li>Clique em "Salvar". Pronto!</li>
                               </ol>`;
                } else if (platform === 'woocommerce') {
                    title = 'Instalando no WooCommerce (WordPress)';
                    content = `<ol style="text-align: left; padding-left: 20px;">
                                 <li>No seu painel WordPress, vá em "Aparência" > "Editor de Arquivos de Tema".</li>
                                 <li>Na lista de temas à direita, certifique-se que seu tema ativo está selecionado.</li>
                                 <li>Na lista de arquivos, encontre e clique em "Rodapé do Tema (footer.php)".</li>
                                 <li>Role até o final e cole o seu código da SynapCortex logo acima da tag <code>&lt;/body&gt;</code>.</li>
                                 <li>Clique em "Atualizar arquivo". Pronto!</li>
                               </ol>`;
                } else if (platform === 'nuvemshop') {
                    title = 'Instalando na Nuvemshop';
                    content = `<ol style="text-align: left; padding-left: 20px;">
                                 <li>No painel da Nuvemshop, acesse "Minha Nuvemshop" > "Layout".</li>
                                 <li>Clique em "Personalizar seu layout".</li>
                                 <li>Vá em "Configurações avançadas" e role até a parte inferior.</li>
                                 <li>Na seção "Códigos de rastreamento externos", cole o seu código da SynapCortex no campo "Rodapé (antes do fechamento da tag body)".</li>
                                 <li>Clique em "Salvar alterações". Pronto!</li>
                               </ol>`;
                } else if (platform === 'universal') {
                    title = 'Instalação Universal (Qualquer Site)';
                    content = `<ol style="text-align: left; padding-left: 20px;">
                                 <li>Abra o arquivo principal do seu site (geralmente index.html).</li>
                                 <li>Localize a tag de fechamento do corpo: <code>&lt;/body&gt;</code>.</li>
                                 <li>Cole o seu código da SynapCortex logo antes dessa tag.</li>
                                 <li>Salve o arquivo e publique no seu servidor. Pronto!</li>
                               </ol>`;
                }
                
                helpModalTitle.innerHTML = title;
                helpModalContent.innerHTML = content;
                helpModal.style.display = 'flex';
            });
        });

        closeModalBtn.onclick = () => { helpModal.style.display = 'none'; };
        window.onclick = event => { if (event.target == helpModal) { helpModal.style.display = 'none'; } };
    }
});