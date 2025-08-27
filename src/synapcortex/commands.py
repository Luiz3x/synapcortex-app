# src/synapcortex/commands.py
import click
from flask.cli import with_appcontext
from .extensions import db, bcrypt
from .models import AppUser, SubscriptionStatus
import secrets

# Cria o grupo de comandos 'admin'
@click.group(name='admin')
def admin_cli():
    """Comandos administrativos para o SynapCortex."""
    pass

# Adiciona o comando 'create-demo-user' ao grupo 'admin'
@admin_cli.command('create-demo-user')
@with_appcontext
def create_demo_user():
    """Cria ou atualiza o usuário de demonstração."""
    demo_email = 'demo@synapcortex.com'
    demo_password = 'demo_password'
    user = AppUser.query.filter_by(email=demo_email).first()
    
    hashed_password = bcrypt.generate_password_hash(demo_password).decode('utf-8')

    if user:
        click.echo(f"Usuário demo '{demo_email}' já existe. Atualizando.")
        user.password_hash = hashed_password
    else:
        click.echo(f"Criando novo usuário demo '{demo_email}'.")
        user = AppUser(
            email=demo_email,
            company_name='Loja de Demonstração',
            password_hash=hashed_password,
            api_key=secrets.token_hex(24),
            subscription_status=SubscriptionStatus.DEMO,
            country='Brasil',
            company_id='00.000.000/0000-00'
        )
        db.session.add(user)
    
    db.session.commit()
    click.echo("Usuário de demonstração processado com sucesso!")

# A FUNÇÃO-CHAVE que exportamos para ser usada em outro lugar
def register_commands(app):
    app.cli.add_command(admin_cli)