# Dentro do arquivo wsgi.py

# Esta linha importa a variável 'app' do seu arquivo principal 'main.py'
from main import app

# Esta linha importa a biblioteca WhiteNoise
from whitenoise import WhiteNoise

# A linha abaixo é a mágica: ela cria uma nova aplicação que, além
# das suas rotas, também sabe servir os arquivos da pasta 'static'.
# O Gunicorn vai usar esta 'application' turbinada.
application = WhiteNoise(app)