// A chave publicável é injetada do Flask para este script
// Ela deve estar disponível como a variável global 'stripe_publishable_key'

const stripe = Stripe(stripe_publishable_key);
const elements = stripe.elements();
const cardElement = elements.create('card');

cardElement.mount('#card-element');

const form = document.getElementById('payment-form');
const cardErrors = document.getElementById('card-errors');
const submitButton = document.getElementById('submit-button');

form.addEventListener('submit', async (event) => {
    event.preventDefault(); // Impede o envio padrão do formulário

    submitButton.disabled = true; // Desabilita o botão para evitar múltiplos cliques

    // Confirma o pagamento no Stripe usando o PaymentIntent.client_secret que recebemos do backend
    const { paymentIntent, error } = await stripe.confirmCardPayment(
        window.clientSecret, // clientSecret virá do backend e será armazenado globalmente
        {
            payment_method: {
                card: cardElement,
                billing_details: {
                    name: 'Nome do Cliente de Teste', // Você pode coletar isso do registro do usuário
                },
            },
        }
    );

    if (error) {
        if (error.type === 'card_error' || error.type === 'validation_error') {
            cardErrors.textContent = error.message;
        } else {
            cardErrors.textContent = 'Um erro inesperado ocorreu.';
        }
        submitButton.disabled = false; // Reabilita o botão
    } else {
        if (paymentIntent.status === 'succeeded') {
            // Pagamento bem-sucedido!
            // Redirecionar para o dashboard ou uma página de sucesso
            alert('Pagamento bem-sucedido! Sua conta foi ativada.');
            window.location.href = '/dashboard'; // Redireciona para o dashboard
        } else {
            // O pagamento não foi bem-sucedido, mas não há erro fatal (ex: pendente)
            cardErrors.textContent = 'Pagamento não concluído. Status: ' + paymentIntent.status;
            submitButton.disabled = false; // Reabilita o botão
        }
    }
});

// --- Lógica para obter o clientSecret do backend ---
// Esta parte precisa ser chamada assim que a página é carregada
// para obter o clientSecret e inicializar o processo de pagamento.
async function fetchClientSecret() {
    try {
        const response = await fetch('/create-payment-intent', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            // Body pode conter dados adicionais se sua rota create-payment-intent precisar
            // body: JSON.stringify({ userId: 'current_user_id' }) 
        });
        const data = await response.json();

        if (data.clientSecret) {
            window.clientSecret = data.clientSecret; // Armazena o clientSecret globalmente
            console.log('Client Secret obtido:', window.clientSecret);
        } else if (data.error) {
            cardErrors.textContent = data.error.message || 'Erro ao obter client secret.';
            submitButton.disabled = true; // Desabilita o botão se não puder obter o client secret
        }
    } catch (e) {
        console.error('Erro na requisição do client secret:', e);
        cardErrors.textContent = 'Erro de comunicação com o servidor.';
        submitButton.disabled = true; // Desabilita o botão em caso de erro de rede
    }
}

// Chama a função para buscar o clientSecret quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', fetchClientSecret);