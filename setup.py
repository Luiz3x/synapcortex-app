# /setup.py (v3.0 - Estrutura "Flat Layout" sem src)
# =================================================================================
# Configuração definitiva para a estrutura de projeto sem a pasta 'src'.
# =================================================================================

from setuptools import setup, find_packages

# Lê o conteúdo do requirements.txt para não duplicar a lista de dependências
try:
    with open('requirements.txt', encoding='utf-8') as f:
        # Continua ignorando a linha '-e .' para evitar o erro de loop
        required = [
            line for line in f.read().splitlines() if not line.startswith('-e')
        ]
except FileNotFoundError:
    required = []

setup(
    name='synapcortex',
    version='2.0.0', # Nova versão maior para refletir a mudança de estrutura
    author='Luiz & Sócio',
    description='SynapCortex - Intelligent Growth Engine for E-commerce',
    
    # --- CORREÇÃO ESTRUTURAL CRÍTICA ---
    # Agora que não há pasta 'src', find_packages() encontra o pacote 'synapcortex'
    # diretamente na raiz do projeto, que é o correto.
    packages=find_packages(), 
    
    include_package_data=True,
    zip_safe=False,
    
    # Usa a lista de dependências já filtrada
    install_requires=required,
)