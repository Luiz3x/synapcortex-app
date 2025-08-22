# synapcortex/config.py

# ... (outras linhas)
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'uma-chave-secreta-muito-forte'
    # AGORA O CÓDIGO LÊ A SENHA DO AMBIENTE, SEM EXPÔ-LA
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///synapcortex.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
# ... (resto do arquivo)