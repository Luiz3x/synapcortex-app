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

    console.log("Usuário está saindo... buscando configuração da API para o pop-up.");
    
    // Busca a configuração do pop-up no backend
    fetch('/api/get-config')
        .then(response => response.json())
        .then(config => {
            // Se o título e a mensagem não estiverem vazios, mostra o pop-up
            if (config.titulo && config.mensagem) {
                document.getElementById('popup-titulo-display').innerText = config.titulo;
                document.getElementById('popup-mensagem-display').innerHTML = config.mensagem;
                document.getElementById('popup-espiao').style.display = 'flex';
            }
        })
        .catch(error => console.error('Erro ao buscar a configuração do pop-up:', error));
}

// "Escuta" o mouse saindo da janela para ativar o pop-up
document.addEventListener('mouseleave', function(event) {
    // A condição event.clientY <= 0 pega o momento que o mouse vai para o topo da tela
    if (event.clientY <= 0) {
        mostrarPopup();
    }
});

// "Escuta" o clique no botão de fechar do pop-up
const fecharBtn = document.getElementById('fechar-popup');
if (fecharBtn) {
    fecharBtn.addEventListener('click', function() {
        document.getElementById('popup-espiao').style.display = 'none';
    });
}


// --- Lógica Principal que Roda Assim que a Página Carrega ---

document.addEventListener('DOMContentLoaded', function() {
    // 1. Gerencia o status do visitante (novo ou recorrente)
    const cookieName = 'synapcortex_visitou';
    const visitanteRecorrente = getCookie(cookieName);

    if (visitanteRecorrente) {
        console.log("Bem-vindo de volta! (Visitante Recorrente)");
        // Futuramente, aqui podemos adicionar uma lógica diferente para recorrentes.
    } else {
        console.log("Olá! (Primeira Visita)");
        setCookie(cookieName, 'true', 365);
    }

    // O código para controlar o modal de login/cadastro já está no seu index.html
    // e deve voltar a funcionar agora que este script está completo e sem erros.
});