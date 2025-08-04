# main.py (Versão de Teste Simplificada)

from flask import Flask, render_template

# Nota: Não estamos importando stripe, SQLAlchemy, etc.
# Mas eles AINDA estarão no requirements.txt e serão instalados pela Render.

app = Flask(__name__)

@app.route('/')
def index():
    # Vamos usar o seu arquivo de teste 'test_css.html' para este experimento.
    # Ele já está na sua pasta 'templates'.
    return render_template('test_css.html')
    