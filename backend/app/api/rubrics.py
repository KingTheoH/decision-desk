from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Rubric, RubricFactor
from app.schemas.rubric import RubricCreate, RubricUpdate, RubricOut, RubricFactorCreate

router = APIRouter(prefix="/rubrics", tags=["rubrics"])


@router.get("", response_model=List[RubricOut])
def list_rubrics(db: Session = Depends(get_db)):
    return db.query(Rubric).order_by(Rubric.created_at.desc()).all()


@router.post("", response_model=RubricOut, status_code=201)
def create_rubric(data: RubricCreate, db: Session = Depends(get_db)):
    rubric = Rubric(
        name=data.name,
        decision_type=data.decision_type,
        description=data.description,
        is_default=data.is_default or False,
    )
    db.add(rubric)
    db.flush()
    for i, f in enumerate(data.factors or []):
        db.add(RubricFactor(rubric_id=rubric.id, sort_order=i, **f.model_dump()))
    db.commit()
    db.refresh(rubric)
    return rubric


@router.get("/{id}", response_model=RubricOut)
def get_rubric(id: str, db: Session = Depends(get_db)):
    r = db.query(Rubric).filter(Rubric.id == id).first()
    if not r:
        raise HTTPException(404)
    return r


@router.patch("/{id}", response_model=RubricOut)
def update_rubric(id: str, data: RubricUpdate, db: Session = Depends(get_db)):
    r = db.query(Rubric).filter(Rubric.id == id).first()
    if not r:
        raise HTTPException(404)
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(r, k, v)
    r.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(r)
    return r


@router.delete("/{id}", status_code=204)
def delete_rubric(id: str, db: Session = Depends(get_db)):
    r = db.query(Rubric).filter(Rubric.id == id).first()
    if not r:
        raise HTTPException(404)
    db.delete(r)
    db.commit()


@router.post("/{id}/factors", status_code=201)
def add_factor(id: str, data: RubricFactorCreate, db: Session = Depends(get_db)):
    r = db.query(Rubric).filter(Rubric.id == id).first()
    if not r:
        raise HTTPException(404)
    count = len(r.factors)
    f = RubricFactor(rubric_id=id, sort_order=count, **data.model_dump())
    db.add(f)
    db.commit()
    db.refresh(f)
    return f


@router.delete("/{id}/factors/{factor_id}", status_code=204)
def delete_factor(id: str, factor_id: str, db: Session = Depends(get_db)):
    f = db.query(RubricFactor).filter(
        RubricFactor.id == factor_id, RubricFactor.rubric_id == id
    ).first()
    if not f:
        raise HTTPException(404)
    db.delete(f)
    db.commit()
