"""
Funções para gerenciamento de senhas.

DEPRECATION NOTICE: verify_password() function has been REMOVED.
Use User.verify_password() method instead.
"""

from passlib.context import CryptContext

# Configuração do contexto de criptografia
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# NOTE: verify_password() function has been REMOVED.
# Use User.verify_password() method instead for password verification.


def get_password_hash(password: str) -> str:
    """
    Gera hash da senha para armazenamento seguro.

    Args:
        password: Senha em texto plano

    Returns:
        Hash da senha para armazenar no banco de dados
    """
    return pwd_context.hash(password)
