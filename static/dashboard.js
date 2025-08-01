document.addEventListener('DOMContentLoaded', () => {
    const configForm = document.getElementById('config-form');

    // Verifica se o formulário de configuração existe na página
    if (configForm) {
        configForm.addEventListener('submit', (event) => {
            // Previne que a página recarregue da forma tradicional
            event.preventDefault();

            // Pega os novos valores dos campos
            const novoTitulo = document.getElementById('popup-titulo').value;
            const novaMensagem = document.getElementById('popup-mensagem').value;

            // Cria um objeto de dados para enviar
            const dadosConfig = {
                popup_titulo: novoTitulo,
                popup_mensagem: novaMensagem
            };

            // Envia os dados para o backend
            fetch('/salvar-configuracoes', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams(dadosConfig)
            })
            .then(response => {
                // Se a resposta do servidor for OK, recarrega a página para mostrar os dados atualizados
                if (response.ok) {
                    console.log("Configurações salvas com sucesso! Recarregando...");
                    window.location.reload();
                } else {
                    alert('Erro: O servidor respondeu com um problema.');
                }
            })
            .catch(error => {
                alert('Erro de comunicação ao salvar as configurações.');
                console.error('Erro ao salvar:', error);
            });
        });
    }
});
