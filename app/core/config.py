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

# --- Configuración de Email ---
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


# Directorio raíz del proyecto (Bi-Centenario-Back)
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
