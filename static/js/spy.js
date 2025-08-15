// =================================================================================
// SYNAPCORTEX - SPY SCRIPT (v6.2 - PRESENTE SURPRESA + CRONÔMETRO)
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
        navigator.sendBeacon(`${backendUrl}api/track`, JSON.stringify({
            apiKey: apiKey, visitorId: visitorId, eventName: eventName, eventData: eventData
        }));
    }

    function showPopup(popupConfig) {
        if (document.getElementById('synapcortex-popup-overlay')) return;

        const overlay = document.createElement('div');
        overlay.id = 'synapcortex-popup-overlay';
        const popup = document.createElement('div');
        popup.id = 'synapcortex-popup';

        const closePopup = () => {
            if (document.body.contains(overlay)) document.body.removeChild(overlay);
            if (document.body.contains(popup)) document.body.removeChild(popup);
        };

        overlay.addEventListener('click', closePopup);
        
        if (popupConfig.abandono_tipo === 'presente') {
            popup.className = 'surprise-popup';
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
                    <div id="synapcortex-timer"></div>
                </div>`;
            
            popup.querySelector('.surprise-content-front').addEventListener('click', function() {
                popup.classList.add('is-flipped');
                
                // Inicia o cronômetro APÓS a revelação
                const timerDuration = (parseInt(popupConfig.abandono_timer_minutos) || 5) * 60;
                startTimer(timerDuration, document.getElementById('synapcortex-timer'));

            }, { once: true });

            popup.querySelector('.close-popup-btn').addEventListener('click', (e) => { e.stopPropagation(); closePopup(); });

        } else { // Pop-up Normal
            popup.className = 'normal-popup';
            popup.innerHTML = `<div class="popup-content"><div class="close-popup-btn">&times;</div><h3>${popupConfig.popup_titulo || 'Atenção!'}</h3><p>${popupConfig.popup_mensagem || 'Temos uma oferta para você.'}</p></div>`;
            popup.querySelector('.close-popup-btn').addEventListener('click', closePopup);
        }

        document.body.appendChild(overlay);
        document.body.appendChild(popup);
        track('popup_exibido', { tipo: popupConfig.abandono_tipo || 'normal' });
    }

    // NOVA FUNÇÃO: Lógica do Cronômetro
    function startTimer(duration, displayElement) {
        let timer = duration, minutes, seconds;
        const interval = setInterval(function () {
            minutes = parseInt(timer / 60, 10);
            seconds = parseInt(timer % 60, 10);

            minutes = minutes < 10 ? "0" + minutes : minutes;
            seconds = seconds < 10 ? "0" + seconds : seconds;

            displayElement.innerHTML = `<span>Sua oferta expira em: <strong>${minutes}:${seconds}</strong></span>`;

            if (--timer < 0) {
                clearInterval(interval);
                displayElement.innerHTML = "<span>Sua oferta expirou!</span>";
            }
        }, 1000);
    }

    // Lógica de Detecção de Abandono
    let mouseLeaveTimer;
    document.addEventListener('mouseleave', function(e) {
        if (e.clientY < 10) {
            if (config.ativar_abandono && !sessionStorage.getItem('synapcortex_popup_shown')) {
                clearTimeout(mouseLeaveTimer);
                mouseLeaveTimer = setTimeout(() => {
                    showPopup(config);
                    sessionStorage.setItem('synapcortex_popup_shown', 'true');
                }, 100);
            }
        }
    });

    // Inicialização
    (function init() {
        fetch(`${backendUrl}api/get-client-config?key=${apiKey}`)
            .then(response => response.json()).then(data => {
                if (!data.error) {
                    config = data;
                    console.log('SynapCortex v2.0: Configurações carregadas.');
                }
            }).catch(err => console.error('SynapCortex: Falha ao buscar configs.', err));
        track('pagina_visitada', { url: window.location.href, title: document.title });
    })();
})();