# =================================================================================
# SYNAPCORTEX - MAIN APPLICATION
# Versão 3.7 - CÓDIGO BLINDADO (À PROVA DE FALHAS)
# =================================================================================
# ... (todas as importações continuam as mesmas) ...

# ... (configuração do App e do DB continua a mesma) ...

# --- MODELOS DO BANCO DE DADOS (FINAL) ---
class AppUser(db.Model):
    # ... (o modelo AppUser com os campos de campanha continua o mesmo) ...
    pass

class AnalyticsEvent(db.Model):
    # ... (o modelo AnalyticsEvent continua o mesmo) ...
    pass

# --- INICIALIZAÇÃO DO BANCO DE DADOS ---
with app.app_context():
    db.create_all()
    # ... (código do usuário demo continua o mesmo) ...

# --- ROTAS DE AUTENTICAÇÃO ---
# ... (rotas de login, registrar, logout continuam as mesmas) ...

# --- ROTA DO PAINEL (BLINDADA) ---
@app.route('/dashboard')
def dashboard():
    if 'logged_in' not in session: return redirect(url_for('index'))
    user = AppUser.query.filter_by(email=session['email']).first()
    if not user: return redirect(url_for('index'))

    # Lógica do painel... (popups, top_pages, etc.)
    
    user_config = json.loads(user.configuracoes or '{}')

    # --- BLINDAGEM DO CÓDIGO ---
    # Verifica se os atributos de campanha existem antes de usá-los
    if not hasattr(user, 'campaign_active'):
        user.campaign_active = False
    if not hasattr(user, 'campaign_config') or user.campaign_config is None:
        user.campaign_config = '{}'
    if not hasattr(user, 'campaign_start_date'):
        user.campaign_start_date = None
    if not hasattr(user, 'campaign_end_date'):
        user.campaign_end_date = None
    # --- FIM DA BLINDAGEM ---

    return render_template('dashboard.html', 
                           usuario=user, 
                           config=user_config, 
                           popups_exibidos=popups_exibidos,
                           top_pages=top_pages,
                           insight_detetive=insight_detetive)

# ... (todas as outras rotas, como /visitors e APIs, continuam as mesmas) ...