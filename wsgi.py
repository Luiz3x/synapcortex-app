# wsgi.py

# Importa a sua aplicação 'app' do arquivo main.py
from main import app

# Importa a biblioteca WhiteNoise
from whitenoise import WhiteNoise

# A linha abaixo "envelopa" sua aplicação e diz ao WhiteNoise
# onde encontrar a pasta 'static'. Esta é a única configuração necessária.
application = WhiteNoise(app, root="static/")