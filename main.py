# main.py - Versão com Memória Permanente (Render Disk)

# --- 1. Importações ---
# Importamos todas as bibliotecas necessárias
import os
import json
from flask import Flask, render_template, request, redirect, url_for, session, flash

# --- 2. Configuração Inicial da Aplicação ---
app = Flask(__name__)
# Chave secreta para gerenciar sessões de login. Pode ser qualquer texto.
app.secret_key = 'sua-chave-secreta-super-dificil'

# --- 3. O CORAÇÃO DA NOSSA MUDANÇA: O DISCO PERMANENTE ---
# Definimos o caminho exato onde nosso arquivo de dados será salvo no disco da Render.
DATA_FILE_PATH = '/var/data/users.json'

# Este bloco de código é o nosso "seguro de vida":
# Ele verifica se a pasta /var/data já existe. Se não existir, ele a cria.
# Isso evita que o programa quebre na primeira vez que tentar salvar um arquivo.
try:
    directory = os.path.dirname(DATA_FILE_PATH)
    if not os.path.exists(directory):
        os.makedirs(directory)
except Exception as e:
    # Se houver um erro ao criar o diretório (raro, mas possível), nós saberemos.
    print(f"ERRO CRÍTICO AO CRIAR DIRETÓRIO: {e}")


# --- 4. Funções Auxiliares para Manipular os Dados ---

def load_users():
    """Carrega os dados dos usuários do nosso disco permanente."""
    try:
        with open(DATA_FILE_PATH, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Se o arquivo não existe ou está vazio/corrompido, retorna um dicionário vazio.
        return {}

def save_users(data):
    """Salva os dados dos usuários no nosso disco permanente."""
    with open(DATA_FILE_PATH, 'w') as f:
        json.dump(data, f, indent=4)


# --- 5. Rotas da Aplicação (As "Páginas" do nosso site) ---

@app.route('/')
def home():
    """Página inicial."""
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html') # Você precisará ter um index.html

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Página de cadastro de novos usuários."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        users = load_users()

        if username in users:
            flash("Este nome de usuário já existe!")
            return redirect(url_for('register'))

        users[username] = {'password': password}
        save_users(users)

        flash("Cadastro realizado com sucesso! Faça o login.")
        return redirect(url_for('login'))

    return render_template('register.html') # Você precisará ter um register.html

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        users = load_users()

        if username in users and users[username]['password'] == password:
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash("Usuário ou senha inválidos.")
            return redirect(url_for('login'))

    return render_template('login.html') # Você precisará ter um login.html

@app.route('/dashboard')
def dashboard():
    """Página protegida, só acessível após o login."""
    if 'username' in session:
        username = session['username']
        return render_template('dashboard.html', user=username) # Você precisará ter um dashboard.html
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    """Rota para fazer logout."""
    session.pop('username', None)
    return redirect(url_for('home'))


# --- 6. Execução da Aplicação ---
# Este bloco faz com que a aplicação rode.
# O host '0.0.0.0' é essencial para funcionar na Render.
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)