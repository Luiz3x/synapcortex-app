# =================================================================================
# SYNAPCORTEX - A CHAVE DE IGNIÇÃO (v2.0)
# Ponto de entrada otimizado para desenvolvimento e produção.
# Utiliza python-dotenv para um gerenciamento de configuração robusto e seguro.
# =================================================================================

import os
import dotenv

# Carrega as variáveis de ambiente do arquivo .env para a sessão atual.
# Isso deve ser feito ANTES de importar a nossa aplicação, para que as
# configurações (como FLASK_CONFIG, DATABASE_URL, etc.) já estejam disponíveis.
dotenv.load_dotenv()

# Importa a nossa função "fábrica" do coração da aplicação.
from synapcortex import create_app

# Cria a instância da aplicação. A função create_app, que aprimoramos,
# agora é inteligente o suficiente para buscar a configuração do ambiente por si só.
# É esta variável 'app' que o Gunicorn (no servidor de produção) irá procurar.
app = create_app()

# --- Bloco de Execução para Desenvolvimento Local ---
# Este bloco só será executado se você rodar o comando "python run.py".
if __name__ == '__main__':
    # Obtém a porta e o host das variáveis de ambiente para maior flexibilidade.
    # '0.0.0.0' permite que a aplicação seja acessível de fora do contêiner/máquina.
    host = os.getenv('FLASK_RUN_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_RUN_PORT', 5000))
    
    # app.run() é o servidor de desenvolvimento do Flask.
    # As configurações de debug são lidas diretamente do config.py.
    app.run(host=host, port=port)