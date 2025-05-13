from cryptography.fernet import Fernet, InvalidToken
from app.core.config import TWO_FACTOR_ENCRYPTION_KEY 


if not TWO_FACTOR_ENCRYPTION_KEY:
    raise ValueError("TWO_FACTOR_ENCRYPTION_KEY no esta configurada La encriptacion 2FA no puede funcionar")

_cipher_suite = Fernet(TWO_FACTOR_ENCRYPTION_KEY)

def encrypt_data(data: str) -> bytes:
    """Encripta una cadena de texto y devuelve los bytes encriptados"""
    if not data:
        return b"" 
    return _cipher_suite.encrypt(data.encode('utf-8'))

def decrypt_data(encrypted_data: bytes) -> str:
    """Desencripta bytes y devuelve la cadena de texto original"""
    if not encrypted_data:
        return "" 
    try:
        return _cipher_suite.decrypt(encrypted_data).decode('utf-8')
    except InvalidToken:
        
        raise ValueError("No se pudieron desencriptar los datos Token invalido") 