from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    INVESTIGADOR = "investigador"
    VISITANTE = "visitante"
