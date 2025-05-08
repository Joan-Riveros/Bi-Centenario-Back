from enum import Enum

class UserRole(str, Enum):
    ADMINISTRADOR = "administrador"
    INVESTIGADOR = "investigador"
    VISITANTE = "visitante"