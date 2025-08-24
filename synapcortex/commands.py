# synapcortex/commands.py
import click
import secrets
from flask.cli import with_appcontext

from .extensions import db, bcrypt
from .models import AppUser, SubscriptionStatus

@click.group(name='admin')
def admin_cli():
    """Comandos administrativos para o SynapCortex."""
    pass

@admin_cli.command('create-demo-user')
@with_appcontext
def create_demo_user():
    """Cria ou atualiza o usuário de demonstração."""
    demo_email = 'demo@synapcortex.com'
    demo_password = 'demo_password' # Senha padrão para o ambiente de desenvolvimento

    user = AppUser.query.filter_by(email=demo_email).first()
    
    hashed_password = bcrypt.generate_password_hash(demo_password).decode('utf-8')

    if user:
        click.echo(f"Usuário demo '{demo_email}' já existe. Atualizando a senha.")
        user.password_hash = hashed_password
    else:
        click.echo(f"Criando novo usuário demo com o e-mail '{demo_email}'.")
        user = AppUser(
            email=demo_email,
            company_name='Loja de Demonstração',
            password_hash=hashed_password,
            country='Brasil',
            company_id='00.000.000/0000-00',
            api_key=secrets.token_hex(24),
            subscription_status=SubscriptionStatus.DEMO
        )
        db.session.add(user)
    
    db.session.commit()
    click.echo("Usuário de demonstração processado com sucesso!")

def register(app):
    """Registra os comandos CLI na aplicação."""
    app.cli.add_command(admin_cli)