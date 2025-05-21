from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import logging

from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash
from app.core.enums import UserRole 

logger = logging.getLogger(__name__)


DEFAULT_ADMIN_EMAIL = "admin@foro.com"
DEFAULT_ADMIN_PASSWORD = "admin123" 

def create_default_admin():
    db: Session = SessionLocal()
    try:
        existing_admin = db.query(User).filter(User.email == DEFAULT_ADMIN_EMAIL).first()
        if existing_admin:
            logger.info(f"El usuario administrador por defecto ({DEFAULT_ADMIN_EMAIL}) ya existe")
            return

        logger.info(f"Creando usuario administrador por defecto: {DEFAULT_ADMIN_EMAIL}")
        admin_user = User(
            email=DEFAULT_ADMIN_EMAIL,
            hashed_password=get_password_hash(DEFAULT_ADMIN_PASSWORD),
            is_active=True,
            nombre="Administrador del Sistema", 
            role=UserRole.ADMINISTRADOR
        )
        db.add(admin_user)
        db.commit()
        logger.info(f"Usuario administrador por defecto ({DEFAULT_ADMIN_EMAIL}) creado exitosamente")

    except IntegrityError:
        logger.error(f"Error de integridad al intentar crear el administrador por defecto. Posiblemente un email duplicado por una condición de carrera")
        db.rollback()
    except Exception as e:
        logger.error(f"Error al crear el usuario administrador por defecto: {e}", exc_info=True)
        db.rollback() 
    finally:
        db.close()

# Para ejecutar este script :
if __name__ == "__main__":
    print("Intentando crear usuario administrador por defecto...")
    create_default_admin()
    print("Proceso finalizado.")