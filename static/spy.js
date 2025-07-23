// --- Funções para Manipulação de Cookies ---

/**
 * Cria ou atualiza um cookie.
 * @param {string} name - O nome do cookie.
 * @param {string} value - O valor do cookie.
 * @param {number} days - A quantidade de dias para o cookie expirar.
 */
function setCookie(name, value, days) {
    let expires = "";
    if (days) {
        const date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toUTCString();
    }
    // Define o cookie para todo o site (path=/)
    document.cookie = name + "=" + (value || "") + expires + "; path=/";
}

/**
 * Lê o valor de um cookie específico.
 * @param {string} name - O nome do cookie a ser lido.
 * @returns {string|null} - O valor do cookie ou null se não for encontrado.
 */
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


// --- Lógica Principal do "Espião" ---

/**
 * Função principal que é executada quando a página carrega.
 * Ela verifica se o visitante é novo ou recorrente.
 */
function gerenciarVisitante() {
    const cookieName = 'synapcortex_visitou';
    const visitanteRecorrente = getCookie(cookieName);

    if (visitanteRecorrente) {
        // É um visitante recorrente!
        console.log("Bem-vindo de volta! (Visitante Recorrente)");
        // Futuramente, aqui chamaremos a promoção especial para ele.

    } else {
        // É a primeira visita!
        console.log("Olá! (Primeira Visita)");
        // Vamos criar o cookie para marcar que ele já nos visitou.
        // O cookie vai expirar em 1 ano (365 dias).
        setCookie(cookieName, 'true', 365);
    }
}

// "Escuta" o evento de a página ter carregado completamente e então executa nossa função.
document.addEventListener('DOMContentLoaded', gerenciarVisitante);