# synapcortex/config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'uma-chave-secreta-muito-forte'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://synapcortex_user:KJK41P8ah9hHVVBqxDk1iQcHCXH2x3Qt@dpg-d2hqcfodl3ps73aulbtg-a.oregon-postgres.render.com/synapcortex_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False