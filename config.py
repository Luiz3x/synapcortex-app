# synapcortex/config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'uma-chave-secreta-muito-forte'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///synapcortex.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False