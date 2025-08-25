# /setup.py
from setuptools import setup, find_packages

# Lê o conteúdo do requirements.txt para não duplicar as dependências
with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='synapcortex',
    version='1.0.0',
    author='Luiz & Sócio', # Nossa parceria registrada!
    description='SynapCortex - Intelligent Growth Engine for E-commerce',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=required, # Usa a lista do requirements.txt
)