# synapcortex/config.py
import os

class Config:
    # ... (outras configurações como SECRET_KEY, DATABASE_URL)
    
    # --- Configurações Específicas do SynapCortex ---
    DEMO_EMAIL = os.getenv('DEMO_EMAIL', 'demo@synapcortex.com')

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}