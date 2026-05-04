from typing import Any, Dict, List

from sqlalchemy import Engine
from sqlalchemy.orm import Session
from BatAnnotation.config import BatAnnotationBase
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def create_all(engine: Engine):
    from BatAnnotation import Tables as _
    from BatAnnotation import Lookup as _
    BatAnnotationBase.metadata.create_all(bind=engine)


def seed_category(db: Session, model: Any, unique_field: str, items_data: List[Dict[Any, Any]]):
    """Безопасно добавляет список объектов, пропуская уже существующие."""
    new_objects = []
    
    for data in items_data:
        exists = db.query(model).filter(
            getattr(model, unique_field) == data[unique_field]
        ).first()
        
        if not exists:
            new_objects.append(model(**data))
            
    if new_objects:
        db.add_all(new_objects)

def connect(path: Path):
    engine = create_engine(f"sqlite:///{path.as_posix()}", echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal, engine