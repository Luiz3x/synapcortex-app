# synapcortex/blueprints/auth/schemas.py
from marshmallow import Schema, fields, validate, ValidationError

# Validador customizado para a senha
def validate_password_complexity(password):
    if not any(char.isupper() for char in password) or \
       not any(char.islower() for char in password) or \
       not any(char.isdigit() for char in password):
        raise ValidationError('A senha deve conter letras maiúsculas, minúsculas e números.')

class RegisterSchema(Schema):
    """ Valida e sanitiza os dados para o registro de um novo usuário. """
    email = fields.Email(required=True, error_messages={"required": "O e-mail é obrigatório."})
    password = fields.Str(required=True, validate=[validate.Length(min=8), validate_password_complexity])
    company_name = fields.Str(required=True, validate=validate.Length(min=2))
    country = fields.Str(required=True)
    cnpj = fields.Str(required=False, allow_none=True) # Permite que seja nulo

class LoginSchema(Schema):
    """ Valida os dados para o login. """
    email = fields.Email(required=True)
    password = fields.Str(required=True)