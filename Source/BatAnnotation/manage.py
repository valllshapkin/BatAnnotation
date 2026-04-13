from sqlalchemy.orm import Session
from BatAnnotation.config import BASE

def create_all(engine):
    from BatAnnotation import Tables as _
    from BatAnnotation import Lookup as _
    BASE.metadata.create_all(bind=engine)


def seed_category(db: Session, model, unique_field: str, items_data: list[dict]):
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