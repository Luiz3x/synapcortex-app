# synapcortex/blueprints/dashboard/routes.py
from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user

from .services import DashboardService, InsightService
# from ...tasks import generate_monthly_report

# --- Blueprint para a PÁGINA (HTML) ---
dashboard_bp = Blueprint(
    'dashboard', 
    __name__, 
    template_folder='../../../templates/dashboard', # Ajuste no caminho
    url_prefix='/dashboard'
)

# --- Blueprint para a API DE DADOS (JSON) ---
dashboard_api_bp = Blueprint(
    'dashboard_api',
    __name__,
    url_prefix='/api/dashboard'
)

# --- Rota da Página ---
@dashboard_bp.route('/home')
@login_required
def home():
    """ Serve a "casca" do painel. Os dados são carregados via API. """
    return render_template('home.html')

# --- Rotas da API ---
@dashboard_api_bp.route('/stats')
@login_required
def get_stats():
    """ Endpoint que fornece as estatísticas principais. """
    stats = DashboardService.get_dashboard_stats(current_user)
    return jsonify({"status": "success", "data": stats})

@dashboard_api_bp.route('/insights')
@login_required
def get_insights():
    """ Endpoint que fornece os insights gerados pelo motor de IA. """
    insights = InsightService.generate_weekly_insights(current_user)
    return jsonify({"status": "success", "data": insights})

@dashboard_api_bp.route('/generate-report', methods=['POST'])
@login_required
def trigger_report_generation():
    """ Inicia a geração de um relatório pesado em segundo plano. """
    # generate_monthly_report.delay(current_user.id)
    return jsonify({
        "status": "accepted", 
        "message": "Seu relatório está sendo gerado. Notificaremos quando estiver pronto."
    }), 202