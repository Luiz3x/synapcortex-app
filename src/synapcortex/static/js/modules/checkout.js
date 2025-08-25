// static/js/modules/checkout.js (v2.0 - Arquitetura com Payment Element)
import { showNotification } from './notifications.js';

/**
 * Orquestra o formulário de pagamento moderno do Stripe usando o Payment Element.
 */
export function initCheckoutForm() {
    const stripePublicKey = window.stripePublicKey;
    const clientSecret = window.clientSecret;

    if (!stripePublicKey || !clientSecret) {
        return; // Sai se não estiver na página de checkout ou se faltar dados.
    }

    const stripe = Stripe(stripePublicKey, { locale: 'pt-BR' });

    const elements = stripe.elements({ clientSecret });

    const paymentElement = elements.create("payment");
    paymentElement.mount("#payment-element");

    const form = document.getElementById('payment-form');
    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        await handlePaymentSubmit(stripe, elements);
    });
}

/**
 * Lida com a submissão do formulário e confirmação do pagamento.
 * @param {object} stripe - A instância do objeto Stripe.
 * @param {object} elements - A instância dos elementos do Stripe.
 */
async function handlePaymentSubmit(stripe, elements) {
    setLoading(true);

    try {
        const { error } = await stripe.confirmPayment({
            elements,
            confirmParams: {
                // A URL para onde o cliente será redirecionado.
                // Corresponde à nossa rota @payments_bp.route('/success')
                return_url: `${window.location.origin}/payments/success`,
            },
        });

        if (error.type === "card_error" || error.type === "validation_error") {
            showMessage(error.message);
        } else {
            showMessage("Ocorreu um erro inesperado. Tente novamente.");
        }
    } catch (e) {
        showMessage("Ocorreu um erro de comunicação. Verifique sua conexão.");
    } finally {
        setLoading(false);
    }
}

// --- Funções Auxiliares de UI ---

function setLoading(isLoading) {
    const submitButton = document.getElementById('submit-button');
    const spinner = document.getElementById('spinner');
    const buttonText = document.getElementById('button-text');

    if (!submitButton || !spinner || !buttonText) return;

    submitButton.disabled = isLoading;
    if (isLoading) {
        spinner.classList.remove('hidden');
        buttonText.classList.add('hidden');
    } else {
        spinner.classList.add('hidden');
        buttonText.classList.remove('hidden');
    }
}

function showMessage(messageText) {
    const messageContainer = document.getElementById("payment-message");
    if (!messageContainer) return;

    messageContainer.classList.remove("hidden");
    messageContainer.textContent = messageText;

    setTimeout(() => {
        messageContainer.classList.add("hidden");
        messageContainer.textContent = "";
    }, 5000);
}