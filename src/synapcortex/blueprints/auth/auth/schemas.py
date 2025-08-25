from marshmallow import Schema, fields, validate, ValidationError

def validate_password_complexity(password):
    if not any(char.isupper() for char in password) or \
       not any(char.islower() for char in password) or \
       not any(char.isdigit() for char in password):
        raise ValidationError('A senha deve conter letras maiúsculas, minúsculas e números.')

class RegisterSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=[validate.Length(min=8), validate_password_complexity])
    company_name = fields.Str(required=True, validate=validate.Length(min=2))
    country = fields.Str(required=True)
    cnpj = fields.Str(required=False, allow_none=True)
    tax_id = fields.Str(required=False, allow_none=True)

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)