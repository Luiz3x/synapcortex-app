# run.py (v5.0 - Arquitetura Final)
# =================================================================================
# SYNAPCORTEX - A CHAVE DE IGNIÇÃO
# Ponto de entrada único e definitivo para a aplicação. Otimizado para
# desenvolvimento local e para produção (Render/Gunicorn).
# =================================================================================

import os
from dotenv import load_dotenv

# PASSO 1: Carrega as variáveis de ambiente do arquivo .env.
# Esta é a PRIMEIRA coisa a ser feita, para que todas as chaves
# (FLASK_CONFIG, DATABASE_URL, etc.) estejam prontas para a aplicação.
load_dotenv()

# PASSO 2: Importa a nossa fábrica de aplicação.
from synapcortex import create_app

# PASSO 3: Cria a instância da aplicação.
# A fábrica `create_app` é inteligente e busca a configuração correta
# (development/production) a partir das variáveis de ambiente.
# É esta variável 'app' que o Gunicorn procura em produção.
app = create_app()

# --- Bloco de Execução Apenas para Desenvolvimento Local ---
# Este trecho só é executado ao rodar o comando "python run.py".
# O Gunicorn na Render ignora este bloco completamente.
if __name__ == '__main__':
    # Obtém host e porta das variáveis de ambiente para maior flexibilidade.
    host = os.getenv('FLASK_RUN_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_RUN_PORT', 5000))
    
    # Inicia o servidor de desenvolvimento do Flask.
    # O modo debug é controlado pela configuração carregada pela `create_app`.
    app.run(host=host, port=port)