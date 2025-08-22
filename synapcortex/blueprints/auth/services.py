# synapcortex/blueprints/auth/services.py
from typing import Dict, Optional
from datetime import datetime, timedelta
import secrets

from ...extensions import db, bcrypt
from ...models import AppUser

class AuthService:
    """ Encapsula toda a lógica de negócios relacionada à autenticação. """

    @staticmethod
    def register_user(data: Dict) -> Optional[AppUser]:
        """
        Cria um novo usuário no sistema.
        Retorna o objeto do usuário criado ou None se o e-mail já existir.
        """
        if AppUser.query.filter_by(email=data['email']).first():
            return None  # Usuário já existe

        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        
        new_user = AppUser(
            email=data['email'],
            company_name=data['company_name'],
            password_hash=hashed_password,
            country=data.get('country'),
            company_id=data.get('cnpj') if data.get('country') == 'BR' else data.get('tax_id', 'N/A'),
            api_key=secrets.token_hex(24), # Aumentado para mais segurança
            trial_end_date=datetime.utcnow() + timedelta(days=30)
        )

        db.session.add(new_user)
        db.session.commit()
        return new_user

    @staticmethod
    def verify_credentials(email: str, password: str) -> Optional[AppUser]:
        """
        Verifica as credenciais de login.
        Retorna o objeto do usuário se as credenciais forem válidas, caso contrário None.
        """
        user = AppUser.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            return user
        return None