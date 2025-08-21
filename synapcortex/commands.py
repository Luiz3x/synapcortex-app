# synapcortex/commands.py
# =================================================================================
# COMANDOS CLI - FERRAMENTAS DE MANUTENÇÃO
# Contém os comandos de terminal para gerenciar a aplicação, como resetar o banco.
# =================================================================================

import click
from flask.cli import with_appcontext
from .extensions import db
from .models import AppUser, AnalyticsEvent # Importe seus modelos aqui

def register(app):
    """Registra todos os comandos CLI com a aplicação Flask."""

    @app.cli.command('reset-db')
    @click.option('--with-seed/--no-seed', default=True, help='Popula o banco com dados demo após o reset.')
    @with_appcontext
    def reset_db_command(with_seed):
        """[CUIDADO] Apaga todos os dados e recria o banco do zero."""
        
        # APRIMORAMENTO: Adiciona uma confirmação real para evitar acidentes.
        click.confirm('Você tem certeza que quer apagar TODO o banco de dados? Esta ação é irreversível.', abort=True)
        
        # CORREÇÃO: Adicionado o bloco 'except' para tratar erros e corrigir a sintaxe.
        try:
            click.secho("-> Apagando todas as tabelas...", fg="yellow")
            db.drop_all()
            
            click.secho("-> Criando a estrutura do banco de dados...", fg="cyan")
            db.create_all()

            if with_seed:
                click.secho("-> Inserindo dados de exemplo (seed)...", fg="cyan")
                # Lógica para adicionar dados de exemplo (semente)
                # Exemplo:
                # user_demo = AppUser(email="demo@exemplo.com", ...)
                # db.session.add(user_demo)
                # db.session.commit()
                pass # Adicione seu código de "seed" aqui se precisar

            click.secho("\nBanco de dados resetado e inicializado com sucesso!", fg="green", bold=True)

        except Exception as e:
            # Em caso de erro, desfaz qualquer alteração pendente
            db.session.rollback()
            click.secho(f"\nERRO: Falha ao resetar o banco de dados.", fg="red", bold=True)
            click.secho(f"Detalhe do erro: {e}", fg="red")

    # Você pode adicionar outros comandos aqui no futuro
    # Ex: @app.cli.command('outro-comando')
    #     def ...