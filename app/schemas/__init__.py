from .user import UserBase # O los que tengas definidos
from .epoca import Epoca, EpocaCreate, EpocaUpdate, EpocaBase
from .region import Region, RegionCreate, RegionUpdate, RegionBase
from .category import Category, CategoryCreate, CategoryUpdate, CategoryBase
from .tag import Tag, TagCreate, TagUpdate, TagBase
from .historical_event import HistoricalEvent, HistoricalEventCreate, HistoricalEventUpdate, HistoricalEventBase
from .document import DocumentMinimal # Añadir esta importación
from .upload_privilege_request import (
    UploadPrivilegeRequest,
    UploadPrivilegeRequestCreate,
    UploadPrivilegeRequestUpdate,
    UploadPrivilegeRequestBase
)
from .document_access_request import (
    DocumentAccessRequest,
    DocumentAccessRequestCreate,
    DocumentAccessRequestUpdate,
    DocumentAccessRequestBase
)
from .document import Document, DocumentCreate, DocumentUpdate, DocumentBase, DocumentMinimal, DocumentLevelUpdate # Añadir DocumentLevelUpdate