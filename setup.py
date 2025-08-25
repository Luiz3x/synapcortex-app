# /setup.py
from setuptools import setup, find_packages

# Lê o conteúdo do requirements.txt para não duplicar a lista de dependências
try:
    with open('requirements.txt', encoding='utf-8') as f:
        # Lê as dependências, mas ignora a linha '-e .'
        required = [
            line for line in f.read().splitlines() if not line.startswith('-e')
        ]
except FileNotFoundError:
    required = []

setup(
    name='synapcortex',
    version='1.0.2', # Nova versão para refletir o ajuste
    author='Luiz & Sócio',
    description='SynapCortex - Intelligent Growth Engine for E-commerce',
    
    # --- AJUSTE: Simplificamos a descoberta de pacotes ---
    # Agora apenas dizemos ONDE procurar, sem remapear o diretório.
    # Isso deve resolver a confusão de caminhos no servidor.
    packages=find_packages(where='src'), 
    
    include_package_data=True,
    zip_safe=False,
    
    # Usa a lista de dependências já filtrada
    install_requires=required,
)