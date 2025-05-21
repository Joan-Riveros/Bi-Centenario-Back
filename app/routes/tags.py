from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import crud, schemas 
from app.core import dependencies

router = APIRouter(
    prefix="/tags",
    tags=["Tags"],
    # dependencies=[Depends(dependencies.get_current_active_user)],
)

@router.post("/", response_model=schemas.tag, status_code=status.HTTP_201_CREATED)
def create_new_tag(
    tag: schemas.TagCreate,
    db: Session = Depends(dependencies.get_db),
    # current_user: models.User = Depends(dependencies.require_investigator_or_admin_user) # O una dependencia similar
):
    db_tag = crud.tag.get_tag_by_name(db, name=tag.name)
    if db_tag:
        return db_tag 
    return crud.tag.create_tag(db=db, obj_in=tag)


@router.get("/", response_model=List[schemas.Tag])
def read_all_tags(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(dependencies.get_db),
    # current_user: models.User = Depends(dependencies.get_current_active_user)
):
    tags = crud.tag.get_tags(db, skip=skip, limit=limit)
    return tags

@router.get("/{tag_id}", response_model=schemas.Tag)
def read_single_tag(
    tag_id: int,
    db: Session = Depends(dependencies.get_db),
    # current_user: models.User = Depends(dependencies.get_current_active_user)
):
    db_tag = crud.tag.get_tag(db, tag_id=tag_id)
    if db_tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    return db_tag

@router.delete("/{tag_id}", response_model=schemas.Tag)
def delete_existing_tag(
    tag_id: int,
    db: Session = Depends(dependencies.get_db),
    # current_user: models.User = Depends(dependencies.require_admin_user) # Solo admins eliminan
):
    db_tag = crud.tag.delete_tag(db, tag_id=tag_id)
    if db_tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    return db_tag