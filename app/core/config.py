from dotenv import load_dotenv
import os
from pathlib import Path 
from fastapi_mail import ConnectionConfig

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Mi Repositorio Historico")
PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = int(os.getenv("PASSWORD_RESET_TOKEN_EXPIRE_HOURS", "1"))

# --- Configuracion de Email ---
MAIL_USERNAME: str = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD")
MAIL_FROM: str = os.getenv("MAIL_FROM")
MAIL_PORT: int = int(os.getenv("MAIL_PORT", 587))
MAIL_SERVER: str = os.getenv("MAIL_SERVER")
MAIL_FROM_NAME: str = os.getenv("MAIL_FROM_NAME", PROJECT_NAME) 
MAIL_STARTTLS: bool = str(os.getenv("MAIL_STARTTLS", "True")).lower() == "true"
MAIL_SSL_TLS: bool = str(os.getenv("MAIL_SSL_TLS", "False")).lower() == "true"
MAIL_USE_CREDENTIALS: bool = bool(MAIL_USERNAME and MAIL_PASSWORD)
MAIL_VALIDATE_CERTS: bool = str(os.getenv("MAIL_VALIDATE_CERTS", "True")).lower() == "true"

FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000") 


# Directorio raiz del proyecto 
PROJECT_ROOT_DIR = Path(__file__).resolve().parent.parent.parent
TEMPLATE_FOLDER_NAME: str = os.getenv("TEMPLATE_FOLDER", "app/templates/email") 
TEMPLATE_ABSOLUTE_PATH = PROJECT_ROOT_DIR / TEMPLATE_FOLDER_NAME

# Configuración de Conexion para fastapi-mail
mail_config = ConnectionConfig(
    MAIL_USERNAME=MAIL_USERNAME,
    MAIL_PASSWORD=MAIL_PASSWORD,
    MAIL_FROM=MAIL_FROM,
    MAIL_PORT=MAIL_PORT,
    MAIL_SERVER=MAIL_SERVER,
    MAIL_FROM_NAME=MAIL_FROM_NAME,
    MAIL_STARTTLS=MAIL_STARTTLS,
    MAIL_SSL_TLS=MAIL_SSL_TLS,
    USE_CREDENTIALS=MAIL_USE_CREDENTIALS,
    VALIDATE_CERTS=MAIL_VALIDATE_CERTS,
    TEMPLATE_FOLDER=TEMPLATE_ABSOLUTE_PATH 
)

#2fa
REMEMBER_DEVICE_COOKIE_NAME: str = "remember_2fa_device"
REMEMBER_DEVICE_TOKEN_EXPIRE_DAYS: int = 30

TWO_FACTOR_ENCRYPTION_KEY: bytes = os.getenv("TWO_FACTOR_ENCRYPTION_KEY", "").encode('utf-8')
if not TWO_FACTOR_ENCRYPTION_KEY:
    
    print("ADVERTENCIA: TWO_FACTOR_ENCRYPTION_KEY no esta configurada. Usando una clave de desarrollo (NO SEGURA).")
    # from cryptography.fernet import Fernet
    # TWO_FACTOR_ENCRYPTION_KEY = Fernet.generate_key() # Solo para desarrollo y si se va a persistir

    
BASE_DIR = Path(__file__).resolve().parent 
MEDIA_ROOT = BASE_DIR.parent / "media"
#Documentos

UPLOAD_DOCUMENTS_DIR: str = os.getenv("UPLOAD_DOCUMENTS_DIR", "media/documents")
UPLOAD_COVERS_DIR: str = os.getenv("UPLOAD_COVERS_DIR", "media/previews")
MAX_DOCUMENT_SIZE_MB = 100
MAX_COVER_SIZE_MB = 5
ALLOWED_DOCUMENT_EXTENSIONS = {".pdf", ".tiff", ".tif", ".jpg", ".jpeg", ".png"}
ALLOWED_COVER_EXTENSIONS = {".jpg", ".jpeg", ".png"}