# /setup.py
from setuptools import setup, find_packages

# Lê o conteúdo do requirements.txt para não duplicar a lista de dependências
try:
    with open('requirements.txt', encoding='utf-8') as f:
        # --- CORREÇÃO FINAL: Lê as dependências, mas ignora a linha '-e .' ---
        required = [
            line for line in f.read().splitlines() if not line.startswith('-e')
        ]
except FileNotFoundError:
    required = []

setup(
    name='synapcortex',
    version='1.0.1', # Incrementado para refletir a correção
    author='Luiz & Sócio', # Nossa parceria registrada!
    description='SynapCortex - Intelligent Growth Engine for E-commerce',
    
    # --- Refinamento: Aponta explicitamente para a pasta 'src' ---
    # Isso garante que o Python encontre nosso pacote da forma mais correta.
    package_dir={'': 'src'},
    packages=find_packages(where='src'), 
    
    include_package_data=True,
    zip_safe=False,
    
    # Usa a lista de dependências já filtrada e corrigida
    install_requires=required,
)