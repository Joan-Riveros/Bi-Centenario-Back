from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import crud, schemas
from app.core import dependencies 

router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)

@router.post("/", response_model=schemas.Category, status_code=status.HTTP_201_CREATED)
def create_new_category(
    category: schemas.CategoryCreate,
    db: Session = Depends(dependencies.get_db),
    # current_user: models.User = Depends(dependencies.require_admin_user) # Solo admins crean
):
    db_category = crud.category.get_category_by_name(db, name=category.name)
    if db_category:
        raise HTTPException(status_code=400, detail="Category with this name already exists")
    return crud.category.create_category(db=db, category=category)

@router.get("/", response_model=List[schemas.Category])
def read_all_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(dependencies.get_db),
    # current_user: models.User = Depends(dependencies.get_current_active_user)
):
    categories = crud.category.get_categories(db, skip=skip, limit=limit)
    return categories

@router.get("/{category_id}", response_model=schemas.Category)
def read_single_category(
    category_id: int,
    db: Session = Depends(dependencies.get_db),
    # current_user: models.User = Depends(dependencies.get_current_active_user)
):
    db_category = crud.category.get_category(db, category_id=category_id)
    if db_category is None:
       raise HTTPException(status_code=404, detail="Category not found")
    return db_category

@router.put("/{category_id}", response_model=schemas.Category)
def update_existing_category(
    category_id: int,
    category_update: schemas.CategoryUpdate,
    db: Session = Depends(dependencies.get_db),
    # current_user: models.User = Depends(dependencies.require_admin_user) 
):
    db_category = crud.category.get_category(db, category_id=category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    if category_update.name and category_update.name != db_category.name:
        existing_category_with_name = crud.category.get_category_by_name(db, name=category_update.name)
    if existing_category_with_name and existing_category_with_name.id != category_id:
        raise HTTPException(status_code=400, detail="Another category with this name already exists")
    return crud.category.update_category(db=db, category_id=category_id, category_update=category_update)

@router.delete("/{category_id}", response_model=schemas.Category)
def delete_existing_category(
    category_id: int,
    db: Session = Depends(dependencies.get_db),
    # current_user: models.User = Depends(dependencies.require_admin_user)
):
    db_category = crud.category.delete_category(db, category_id=category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category