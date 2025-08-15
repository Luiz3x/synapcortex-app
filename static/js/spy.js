// =================================================================================
// SYNAPCORTEX - SPY SCRIPT (v5.0 - FLIP 3D E OVERLAY)
// =================================================================================
(function() {
    const scriptTag = document.getElementById('synapcortex-spy-script');
    if (!scriptTag) { console.error('SynapCortex: Script tag não encontrado.'); return; }
    
    const apiKey = scriptTag.getAttribute('src').split('key=')[1].split('&')[0];
    const backendUrl = scriptTag.getAttribute('data-backend-url');
    let visitorId = localStorage.getItem('synapcortex_visitor_id');
    let config = {};

    if (!visitorId) {
        visitorId = Date.now().toString(36) + Math.random().toString(36).substr(2);
        localStorage.setItem('synapcortex_visitor_id', visitorId);
    }

    function track(eventName, eventData = {}) {
        // Usa sendBeacon para envio assíncrono que não bloqueia a página
        navigator.sendBeacon(`${backendUrl}api/track`, JSON.stringify({
            apiKey: apiKey,
            visitorId: visitorId,
            eventName: eventName,
            eventData: eventData
        }));
    }

    function showPopup(popupConfig) {
        // Previne múltiplos pop-ups
        if (document.getElementById('synapcortex-popup-overlay')) return;

        const overlay = document.createElement('div');
        overlay.id = 'synapcortex-popup-overlay';

        const popup = document.createElement('div');
        popup.id = 'synapcortex-popup';

        const closePopup = () => {
            document.body.removeChild(overlay);
            document.body.removeChild(popup);
        };

        overlay.addEventListener('click', closePopup);
        
        if (popupConfig.abandono_tipo === 'presente') {
            popup.className = 'surprise-popup';
            // Monta a frente do cartão
            popup.innerHTML = `
                <div class="surprise-content-front">
                    <div class="surprise-icon">🎁</div>
                    <p>${popupConfig.abandono_presente_fechado || 'Um presente para você!'}</p>
                    <small>Clique para revelar</small>
                </div>
                <div class="surprise-content-back">
                    <div class="close-popup-btn">&times;</div>
                    <div class="surprise-icon">🎉</div>
                    <p>${popupConfig.abandono_presente_aberto || 'Cupom revelado!'}</p>
                </div>`;
            
            // Lógica do clique para virar
            const front = popup.querySelector('.surprise-content-front');
            front.addEventListener('click', function() {
                popup.classList.add('is-flipped');
            }, { once: true });

            // Lógica para fechar no verso
            popup.querySelector('.close-popup-btn').addEventListener('click', (e) => {
                e.stopPropagation(); // Previne que o clique feche o overlay também
                closePopup();
            });

        } else { // Pop-up Normal
            popup.className = 'normal-popup';
            popup.innerHTML = `
                <div class="popup-content">
                    <div class="close-popup-btn">&times;</div>
                    <h3>${popupConfig.popup_titulo || 'Atenção!'}</h3>
                    <p>${popupConfig.popup_mensagem || 'Temos uma oferta para você.'}</p>
                </div>`;
            popup.querySelector('.close-popup-btn').addEventListener('click', closePopup);
        }

        document.body.appendChild(overlay);
        document.body.appendChild(popup);
        track('popup_exibido', { tipo: popupConfig.abandono_tipo || 'normal' });
    }

    // Lógica de Detecção de Abandono (intenção de saída)
    let mouseLeaveTimer;
    document.addEventListener('mouseleave', function(e) {
        if (e.clientY < 10) { // Dispara se o mouse subir perto do topo
            if (config.ativar_abandono && !sessionStorage.getItem('synapcortex_popup_shown')) {
                clearTimeout(mouseLeaveTimer);
                mouseLeaveTimer = setTimeout(() => {
                    showPopup(config);
                    sessionStorage.setItem('synapcortex_popup_shown', 'true'); // Mostra só uma vez por sessão
                }, 100);
            }
        }
    });

    // Inicialização do script
    (function init() {
        fetch(`${backendUrl}api/get-client-config?key=${apiKey}`)
            .then(response => response.json())
            .then(data => {
                if (!data.error) {
                    config = data;
                    console.log('SynapCortex v2.0: Configurações carregadas com sucesso.');
                } else {
                    console.error('SynapCortex Error:', data.error);
                }
            })
            .catch(err => console.error('SynapCortex: Falha ao buscar configurações.', err));

        track('pagina_visitada', { url: window.location.href, title: document.title });
    })();

})();