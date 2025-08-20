# synapcortex/config.py

import os
from dotenv import load_dotenv
from pathlib import Path

# Carrega as variáveis de ambiente de um arquivo .env na raiz do projeto.
# Isso mantém suas chaves secretas e configurações sensíveis fora do código.
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    """
    Configurações base, herdadas por todas as outras classes de configuração.
    Contém valores padrão e configurações que não mudam entre os ambientes.
    """
    # Chave secreta para segurança da sessão. Essencial para proteger contra ataques CSRF.
    # O aplicativo irá falhar ao iniciar se esta chave não for definida no ambiente.
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("A SECRET_KEY não foi definida. Por favor, configure no seu arquivo .env")

    # Desativa um recurso de sinalização de eventos do SQLAlchemy que não é necessário
    # e consome recursos. É uma boa prática desativá-lo explicitamente.
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Chaves da API do Stripe, carregadas do ambiente para segurança.
    STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')


class ProductionConfig(Config):
    """
    Configurações para o ambiente de PRODUÇÃO (executando no Render.com).
    Aqui, a segurança e a eficiência são máximas.
    """
    DEBUG = False
    TESTING = False

    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        raise ValueError("A DATABASE_URL não foi definida para o ambiente de produção.")

    # Converte 'postgres://' para 'postgresql://' para compatibilidade com SQLAlchemy.
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = db_url

    # Exige SSL para conexões com o banco de dados em produção, uma camada extra de segurança.
    SQLALCHEMY_ENGINE_OPTIONS = {'connect_args': {'sslmode': 'require'}}


class DevelopmentConfig(Config):
    """
    Configurações para o ambiente de DESENVOLVIMENTO (no seu computador).
    O foco aqui é a facilidade de debug e a rapidez nos testes.
    """
    DEBUG = True

    # No desenvolvimento, usa a DATABASE_URL_DEV do .env se existir,
    # senão, cria um banco de dados SQLite local para facilitar testes rápidos sem precisar do PostgreSQL.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL_DEV', 'sqlite:///../synapcortex_local.db')


class TestingConfig(Config):
    """
    Configurações para o ambiente de TESTES AUTOMATIZADOS.
    O foco é a velocidade e o isolamento, para que os testes não afetem outros bancos.
    """
    TESTING = True
    DEBUG = True

    # Para testes, usamos um banco de dados SQLite em memória para que os testes
    # sejam super rápidos e não deixem nenhum lixo para trás.
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Desativa a proteção CSRF durante os testes para simplificar as requisições.
    WTF_CSRF_ENABLED = False
    
    # Usa uma chave secreta simples e fixa para os testes.
    SECRET_KEY = 'testing-secret-key'


# Dicionário que mapeia o nome do ambiente para a classe de configuração correspondente.
# Facilita carregar a configuração correta no arquivo principal da aplicação.
config_by_name = dict(
    development=DevelopmentConfig,
    testing=TestingConfig,
    production=ProductionConfig
)