from sqlalchemy.orm import Session
from BatAnnotation.manage import seed_category
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
        {"code": "forest", "name_ru": "Лес", "name_en": "Forest"},
        {"code": "forest_edge", "name_ru": "Опушка леса", "name_en": "Forest Edge"},
        {"code": "water", "name_ru": "Водоём", "name_en": "Water Body"},
        {"code": "field", "name_ru": "Поле / Луг", "name_en": "Field / Meadow"},
        {"code": "urban", "name_ru": "Городская среда", "name_en": "Urban"},
        {"code": "wetland", "name_ru": "Болото", "name_en": "Wetland"},
        {"code": "unknown", "name_ru": "Неизвестно", "name_en": "Unknown"},
    ]
    seed_category(db, HabitatType, "code", data)

def seed_contexts(db: Session):
    data = [
        {"code": "foraging", "name_ru": "Охота", "name_en": "Foraging"},
        {"code": "commuting", "name_ru": "Перелёт", "name_en": "Commuting"},
        {"code": "roosting", "name_ru": "Убежище", "name_en": "Roosting"},
        {"code": "social", "name_ru": "Социальные сигналы", "name_en": "Social"},
        {"code": "drinking", "name_ru": "Питьё", "name_en": "Drinking"},
        {"code": "unknown", "name_ru": "Неизвестно", "name_en": "Unknown"},
    ]
    seed_category(db, ContextType, "code", data)

def seed_shapes(db: Session):
    data = [
        {"code": "FM", "name_ru": "Частотно-модулированный"},
        {"code": "CF", "name_ru": "Постоянная частота"},
        {"code": "qCF", "name_ru": "Квазипостоянная частота"},
        {"code": "FM-qCF", "name_ru": "FM с квазипостоянным хвостом"},
        {"code": "qCF-FM", "name_ru": "Квазипостоянный с FM хвостом"},
        {"code": "FM-CF-FM", "name_ru": "FM-CF-FM составной"},
    ]
    seed_category(db, SignalShape, "code", data)

def seed_all(db: Session):
    """Вызывать всегда, в любом проекте"""
    seed_detectors(db)
    seed_habitats(db)
    seed_contexts(db)
    seed_shapes(db)
    db.commit()