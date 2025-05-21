from .crud_upload_privilege_request import (
    get_upload_privilege_request,
    get_upload_privilege_requests_by_user,
    get_pending_upload_request_by_user_and_title,
    get_all_upload_privilege_requests,
    create_upload_privilege_request,
    
    remove_upload_privilege_request
)
from .crud_document_access_request import (
    get_document_access_request,
    get_document_access_requests_by_user,
    get_document_access_requests_for_document,
    get_pending_document_access_request,
    get_approved_document_access_request,
    get_all_document_access_requests,
    create_document_access_request,
    update_document_access_request,
    remove_document_access_request
)
from .crud_epoca import (
    get_epoca,
    get_epocas,
    create_epoca,
    update_epoca,
    remove_epoca
)
from .crud_region import (
    get_region,
    get_regiones,
    create_region,
    update_region,
    remove_region
)
from .crud_category import (
    get_category,
    get_category_by_name,
    get_categories,
    create_category,
    update_category,
    remove_category
)   
from .crud_tag import (
    get_tag,
    get_tag_by_name,
    get_tags,
    create_tag,
    update_tag,
    remove_tag
)   
from .crud_document import (
    get_document,
    get_documents,
    create_document,
    update_document,
    remove_document
)   
from .crud_historical_event import (
    get_historical_event,
    get_historical_events,
    create_historical_event,
    update_historical_event,
    remove_historical_event
)

from .crud_rating import (
    get_rating,
    get_rating_by_user_and_document,
    get_ratings_by_user,
    get_ratings_for_document,
    create_rating,
    update_rating,
    remove_rating,
    remove_rating_by_user_and_document
)