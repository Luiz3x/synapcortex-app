# wsgi.py (Versão "Caça-Fantasmas")

from main import app
from whitenoise import WhiteNoise
import os

# Cria o caminho absoluto para a pasta 'static'.
static_path = os.path.join(os.path.dirname(__file__), 'static')

# Envolve a aplicação Flask com o WhiteNoise.
application = WhiteNoise(app)

# Adiciona explicitamente os arquivos da sua pasta static, servindo-os sob o prefixo '/static/'
application.add_files(static_path, prefix='static/')