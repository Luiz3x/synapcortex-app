// Flag para garantir que o pop-up só seja mostrado uma vez por visita
let popupMostrado = false;

// Função principal para mostrar o pop-up
function mostrarPopup() {
    // Se já mostrou, não faz nada
    if (popupMostrado) return;
    popupMostrado = true;

    console.log("Usuário está saindo... buscando configuração da API.");

    // Busca a configuração do pop-up no backend
    fetch('/api/get-config')
        .then(response => response.json())
        .then(config => {
            console.log("Configuração recebida:", config);

            // Atualiza e mostra o pop-up
            document.getElementById('popup-titulo-display').innerText = config.titulo;
            document.getElementById('popup-mensagem-display').innerHTML = config.mensagem;
            document.getElementById('popup-espiao').style.display = 'flex';
        })
        .catch(error => console.error('Erro ao buscar a configuração:', error));
}

// "Escuta" o mouse saindo da janela para ativar o pop-up
document.addEventListener('mouseleave', function(event) {
    if (event.clientY <= 0) {
        mostrarPopup();
    }
});

// "Escuta" o clique no botão de fechar do pop-up
// Adicionamos uma verificação para ver se o botão existe antes de adicionar o listener
const fecharBtn = document.getElementById('fechar-popup');
if (fecharBtn) {
    fecharBtn.addEventListener('click', function() {
        document.getElementById('popup-espiao').style.display = 'none';
    });
}