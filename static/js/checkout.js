// =================================================================================
// SYNAPCORTEX - LÓGICA DO CHECKOUT (v1.0)
// =================================================================================
document.addEventListener('DOMContentLoaded', () => {
    // A chave publicável é passada para a variável 'stripePublicKey' pelo template HTML
    if (typeof stripePublicKey === 'undefined') {
        console.error('Chave publicável do Stripe não encontrada.');
        return;
    }

    const stripe = Stripe(stripePublicKey);

    const elements = stripe.elements();
    const cardElement = elements.create('card', {
        style: {
            base: {
                color: '#f0f0f5',
                fontFamily: '"Poppins", sans-serif',
                fontSmoothing: 'antialiased',
                fontSize: '16px',
                '::placeholder': {
                    color: '#a0a0c0'
                }
            },
            invalid: {
                color: '#dc3545',
                iconColor: '#dc3545'
            }
        }
    });
    cardElement.mount('#card-element');

    const form = document.getElementById('payment-form');
    const submitButton = document.getElementById('submit-button');
    const spinner = document.getElementById('spinner');
    const buttonText = document.getElementById('button-text');
    const cardErrors = document.getElementById('card-errors');

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        // Desabilita o botão e mostra o spinner
        submitButton.disabled = true;
        spinner.classList.remove('hidden');
        buttonText.classList.add('hidden');
        cardErrors.textContent = '';

        try {
            // Passo 2 (Backend): Buscar o 'clientSecret' do nosso servidor
            // Esta rota ainda vamos construir no main.py
            const response = await fetch('/create-payment-intent', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
            });
            const { clientSecret, error: backendError } = await response.json();

            if (backendError) {
                cardErrors.textContent = backendError;
                revertButtonState();
                return;
            }

            // Passo 3 (Frontend -> Stripe): Confirmar o pagamento
            const { paymentIntent, error: stripeError } = await stripe.confirmCardPayment(clientSecret, {
                payment_method: {
                    card: cardElement
                }
            });

            if (stripeError) {
                cardErrors.textContent = stripeError.message;
                revertButtonState();
                return;
            }

            // Sucesso! O pagamento foi processado.
            console.log('Pagamento bem-sucedido:', paymentIntent);
            buttonText.textContent = 'Pagamento Aprovado!';
            spinner.classList.add('hidden');
            buttonText.classList.remove('hidden');
            
            // Redireciona para o dashboard com uma mensagem de boas-vindas
            window.location.href = '/dashboard?payment=success';

        } catch (error) {
            console.error('Erro inesperado no checkout:', error);
            cardErrors.textContent = 'Ocorreu um erro inesperado. Por favor, tente novamente.';
            revertButtonState();
        }
    });

    function revertButtonState() {
        submitButton.disabled = false;
        spinner.classList.add('hidden');
        buttonText.classList.remove('hidden');
    }
});