from sqlalchemy.orm import Session
from BatAnnotation.API.DataBase import seed_category
from BatAnnotation.Lookup import DetectorModel, HabitatType, ContextType, SignalShape

def seed_detectors(db: Session):
    data = [
        {"manufacturer": "Pettersson", "model": "D500x", "detector_type": "full_spectrum", "sample_rate_hz": 500000},
        {"manufacturer": "Wildlife Acoustics", "model": "SM4BAT", "detector_type": "full_spectrum", "sample_rate_hz": 384000},
        {"manufacturer": "Titley Scientific", "model": "Anabat Swift", "detector_type": "zero_crossing"},
        {"manufacturer": "Open Acoustic Devices", "model": "AudioMoth", "detector_type": "full_spectrum", "sample_rate_hz": 384000},
    ]
    seed_category(db, DetectorModel, "model", data)

def seed_habitats(db: Session):
    data = [
        {"code": "forest", "name": "Forest"},
        {"code": "forest_edge", "name": "Forest Edge"},
        {"code": "water", "name": "Water Body"},
        {"code": "field", "name": "Field / Meadow"},
        {"code": "urban", "name": "Urban"},
        {"code": "wetland", "name": "Wetland"},
        {"code": "unknown", "name": "Unknown"},
    ]
    seed_category(db, HabitatType, "code", data)

def seed_contexts(db: Session):
    data = [
        {"code": "foraging", "name": "Foraging"},
        {"code": "commuting", "name": "Commuting"},
        {"code": "roosting", "name": "Roosting"},
        {"code": "social", "name": "Social"},
        {"code": "drinking", "name": "Drinking"},
        {"code": "unknown", "name": "Unknown"},
    ]
    seed_category(db, ContextType, "code", data)

def seed_shapes(db: Session):
    data = [
        {"code": "FM", "name": "Frequency Modulated"},
        {"code": "CF", "name": "Constant Frequency"},
        {"code": "qCF", "name": "Quasi-Constant Frequency"},
        {"code": "FM-qCF", "name": "FM with qCF tail"},
        {"code": "qCF-FM", "name": "qCF with FM tail"},
        {"code": "FM-CF-FM", "name": "FM-CF-FM compound"},
    ]
    seed_category(db, SignalShape, "code", data)

def seed_all(db: Session):
    """Вызывать всегда, в любом проекте"""
    seed_detectors(db)
    seed_habitats(db)
    seed_contexts(db)
    seed_shapes(db)
    db.commit()
