from enum import Enum

class UserRole(str, Enum):
    ADMINISTRADOR = "administrador"
    INVESTIGADOR = "investigador"
    VISITANTE = "visitante"


class OCRStatusEnum(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


#permisos
class RequestStatusEnum(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"