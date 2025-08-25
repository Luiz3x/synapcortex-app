# /setup.py (v4.0 - Estrutura "SRC Layout" Definitiva)
from setuptools import setup, find_packages

try:
    with open('requirements.txt', encoding='utf-8') as f:
        required = [
            line for line in f.read().splitlines() if not line.startswith('-e')
        ]
except FileNotFoundError:
    required = []

setup(
    name='synapcortex',
    version='3.0.0', # Nova versão para a arquitetura final
    author='Luiz & Sócio',
    description='SynapCortex - Intelligent Growth Engine for E-commerce',
    
    # A configuração correta para o "src layout"
    package_dir={'': 'src'},
    packages=find_packages(where='src'), 
    
    include_package_data=True,
    zip_safe=False,
    install_requires=required,
)