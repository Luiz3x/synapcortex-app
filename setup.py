# /setup.py
from setuptools import setup, find_packages

# Lê o conteúdo do requirements.txt para não duplicar a lista de dependências
try:
    with open('requirements.txt', encoding='utf-8') as f:
        required = f.read().splitlines()
except FileNotFoundError:
    required = []

setup(
    name='synapcortex',
    version='1.0.0',
    author='Luiz & Sócio', # Nossa parceria registrada!
    description='SynapCortex - Intelligent Growth Engine for E-commerce',
    
    # Encontra nosso pacote 'synapcortex' automaticamente na raiz do projeto
    packages=find_packages(), 
    
    include_package_data=True,
    zip_safe=False,
    
    # Usa a lista de dependências lida do requirements.txt
    install_requires=required,
)