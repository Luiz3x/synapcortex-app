# wsgi.py (Versão FINAL E CORRIGIDA)

from main import app
from whitenoise import WhiteNoise

# O WhiteNoise "envolve" nossa aplicação principal para gerenciar os arquivos estáticos.
# O mais importante é que o resultado final continue na variável 'app'.
# Assim, a Render encontra exatamente o que o comando 'gunicorn wsgi:app' está procurando.
app = WhiteNoise(app, root='static/')