// static/js/checkout.js

document.addEventListener('DOMContentLoaded', () => {
    // A chave publicável é injetada do template HTML
    const stripe = Stripe(stripe_publishable_key);
    
    // Configurações visuais do campo do cartão
    const elements = stripe.elements({
        style: {
            base: {
                color: '#f0f0f0',
                fontFamily: '"Poppins", sans-serif',
                fontSize: '16px',
                '::placeholder': {
                    color: '#a0a0a0'
                }
            },
            invalid: {
                color: '#ff4d4d',
                iconColor: '#ff4d4d'
            }
        }
    });

    const cardElement = elements.create('card');
    cardElement.mount('#card-element');

    const form = document.getElementById('payment-form');
    const submitButton = document.getElementById('submit-button');
    const cardErrors = document.getElementById('card-errors');

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        submitButton.disabled = true;
        submitButton.textContent = 'Processando...';
        cardErrors.textContent = '';

        // Pede ao nosso backend para criar uma intenção de pagamento
        const response = await fetch('/create-payment-intent', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ amount: 9990 }) // R$ 99,90 em centavos
        });
        const { clientSecret, error: backendError } = await response.json();

        if (backendError) {
            cardErrors.textContent = backendError.message;
            submitButton.disabled = false;
            submitButton.textContent = 'Pagar Assinatura (R$ 99,90/mês)';
            return;
        }

        // Confirma o pagamento no Stripe usando o clientSecret
        const { paymentIntent, error: stripeError } = await stripe.confirmCardPayment(
            clientSecret, {
                payment_method: {
                    card: cardElement
                }
            }
        );

        if (stripeError) {
            cardErrors.textContent = stripeError.message;
            submitButton.disabled = false;
            submitButton.textContent = 'Pagar Assinatura (R$ 99,90/mês)';
        } else if (paymentIntent.status === 'succeeded') {
            // Pagamento bem-sucedido!
            // Avisa o backend que o pagamento foi um sucesso
            fetch('/payment-success', { method: 'POST' })
                .then(() => {
                    window.location.href = '/dashboard';
                });
        }
    });
});