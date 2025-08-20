# =================================================================================
# SYNAPCORTEX - A CHAVE DE IGNIÇÃO (v3.0 - Unificado e Inteligente)
# Ponto de entrada único, otimizado para desenvolvimento e produção.
# Carrega as variáveis de ambiente do arquivo .env antes de qualquer outra operação.
# =================================================================================

import os
from dotenv import load_dotenv

# APRIMORAMENTO: Garante que o carregamento do .env seja a primeira coisa a acontecer.
# Isso torna as configurações (FLASK_CONFIG, DATABASE_URL, etc.) disponíveis
# para a nossa fábrica de aplicação desde o início.
load_dotenv()

# Importa a nossa função "fábrica" do coração da aplicação.
from synapcortex import create_app

# Cria a instância da aplicação. A fábrica `create_app` é inteligente e busca
# a configuração correta a partir das variáveis de ambiente.
# É esta variável 'app' que o Gunicorn (em produção) irá procurar.
app = create_app()

# --- Bloco de Execução Apenas para Desenvolvimento Local ---
# Este trecho só é executado ao rodar o comando "python run.py".
# Em produção, o servidor WSGI (Gunicorn) chama a variável 'app' diretamente.
if __name__ == '__main__':
    # APRIMORAMENTO: Obtém host e porta das variáveis de ambiente,
    # tornando o ambiente de desenvolvimento muito mais flexível.
    # O padrão para 'host' foi alterado para '127.0.0.1' por ser mais seguro.
    host = os.getenv('FLASK_RUN_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_RUN_PORT', 5000))
    
    # O modo debug é ativado ou desativado pela configuração que a `create_app`
    # carrega, tornando este comando seguro e adaptável.
    app.run(host=host, port=port)