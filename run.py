# =================================================================================
# SYNAPCORTEX - A CHAVE DE IGNIÇÃO (APLICAÇÃO PRINCIPAL FLASK)
# Ponto de entrada único para a aplicação do usuário (Dashboard, Auth, etc.).
# =================================================================================

import os
from dotenv import load_dotenv

# PASSO 1: Carrega as variáveis de ambiente do arquivo .env.
# Deve ser a primeira coisa a ser feita.
load_dotenv()

# PASSO 2: Importa a nossa fábrica de aplicação e as extensões necessárias.
# --- CORREÇÃO: Removido o prefixo 'src.' para compatibilidade com a estrutura do projeto ---
from synapcortex import create_app
from synapcortex.extensions import socketio

# PASSO 3: Cria a instância da aplicação Flask.
# É esta variável 'app' que o Gunicorn (servidor de produção) procura.
app = create_app()

# --- Bloco de Execução Apenas para Desenvolvimento Local ---
# Este trecho só é executado ao rodar o comando "python3 run.py".
if __name__ == '__main__':
    # Obtém host e porta das variáveis de ambiente para maior flexibilidade.
    host = os.getenv('FLASK_RUN_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_RUN_PORT', 5000))
    
    # Inicia o servidor de desenvolvimento usando o SocketIO para habilitar o tempo real.
    # Usar socketio.run() em vez de app.run() é a forma correta.
    socketio.run(app, host=host, port=port)