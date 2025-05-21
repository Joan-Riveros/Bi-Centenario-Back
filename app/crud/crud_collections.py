from typing import List, Optional, Union, Dict, Any
from sqlalchemy.orm import Session

from app.models.collection import Collection
from app.models.document import Document 
from app.schemas.collection import CollectionCreate, CollectionUpdate

def get_collection(db: Session, collection_id: int) -> Optional[Collection]:

    return db.query(Collection).filter(Collection.id == collection_id).first()

def get_collection_by_name_and_user(
    db: Session, *, name: str, user_id: int
) -> Optional[Collection]:

    return db.query(Collection).filter(Collection.name == name, Collection.user_id == user_id).first()


def get_collections_by_user(
    db: Session, user_id: int, skip: int = 0, limit: int = 100
) -> List[Collection]:

    return (
        db.query(Collection)
        .filter(Collection.user_id == user_id)
        .order_by(Collection.name.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_collection(db: Session, *, obj_in: CollectionCreate, user_id: int) -> Collection:

    collection_data = {
        "name": obj_in.name,
        "description": obj_in.description,
        "user_id": user_id
    }
    db_obj = Collection(**collection_data)

    if obj_in.document_ids:
        documents_to_add = db.query(Document).filter(Document.id.in_(obj_in.document_ids)).all()
        db_obj.documents = documents_to_add 

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_collection(
    db: Session, *, db_obj: Collection, obj_in: Union[CollectionUpdate, Dict[str, Any]]
) -> Collection:

    if isinstance(obj_in, dict):
        update_data = obj_in

        document_ids_to_set = update_data.pop("document_ids", None)
    else:
        update_data = obj_in.model_dump(exclude_unset=True, exclude={"document_ids"})
        document_ids_to_set = obj_in.document_ids if hasattr(obj_in, "document_ids") else None



    for field, value in update_data.items():
        setattr(db_obj, field, value)


    if document_ids_to_set is not None: 
        if document_ids_to_set:
            documents_to_set = db.query(Document).filter(Document.id.in_(document_ids_to_set)).all()
            db_obj.documents = documents_to_set
        else:
            db_obj.documents = [] 

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def add_document_to_collection(
    db: Session, *, db_obj_collection: Collection, db_obj_document: Document
) -> Collection:

    if db_obj_document not in db_obj_collection.documents:
        db_obj_collection.documents.append(db_obj_document)
        db.add(db_obj_collection)
        db.commit()
        db.refresh(db_obj_collection)
    return db_obj_collection

def remove_document_from_collection(
    db: Session, *, db_obj_collection: Collection, db_obj_document: Document
) -> Collection:

    if db_obj_document in db_obj_collection.documents:
        db_obj_collection.documents.remove(db_obj_document)
        db.add(db_obj_collection)
        db.commit()
        db.refresh(db_obj_collection)
    return db_obj_collection


def remove_collection(db: Session, *, collection_id: int) -> Optional[Collection]:

    db_obj = db.query(Collection).get(collection_id)
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj
