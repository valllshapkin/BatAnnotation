# = = = = = INNER = = = = = =
from BatAnnotation import config as BatAnnotationConfig
BatAnnotationConfig.test()
# = = = = = INNER = = = = = =

from typing import Optional
import uuid

from sqlalchemy import String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from BatAnnotation.config import BASE

class Species(BASE):
    """Виды летучих мышей"""
    __tablename__ = 'ref_species'

    species_id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    latin_name: Mapped[str] = mapped_column(String, unique=True, nullable=False)   # Pipistrellus pipistrellus
    common_name_ru: Mapped[Optional[str]] = mapped_column(String, nullable=True)   # Нетопырь-карлик
    common_name_en: Mapped[Optional[str]] = mapped_column(String, nullable=True)   # Common Pipistrelle
    family: Mapped[Optional[str]] = mapped_column(String, nullable=True)           # Vespertilionidae
    genus: Mapped[Optional[str]] = mapped_column(String, nullable=True)            # Pipistrellus
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)                 # можно скрыть устаревшие
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)


class DetectorModel(BASE):
    """Модели детекторов"""
    __tablename__ = 'ref_detector_models'

    detector_id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    manufacturer: Mapped[str] = mapped_column(String)           # Pettersson
    model: Mapped[str] = mapped_column(String, unique=True)     # D500x
    detector_type: Mapped[str] = mapped_column(String)          # full_spectrum / zero_crossing / time_expansion
    sample_rate_hz: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)


class HabitatType(BASE):
    """Типы местообитаний"""
    __tablename__ = 'ref_habitat_types'

    habitat_id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    code: Mapped[str] = mapped_column(String, unique=True)      # forest_edge
    name_ru: Mapped[str] = mapped_column(String)                # Опушка леса
    name_en: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class ContextType(BASE):
    """Типы поведенческих контекстов"""
    __tablename__ = 'ref_context_types'

    context_id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    code: Mapped[str] = mapped_column(String, unique=True)      # foraging
    name_ru: Mapped[str] = mapped_column(String)                # Охота
    name_en: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class SignalShape(BASE):
    """Формы сигналов"""
    __tablename__ = 'ref_signal_shapes'

    shape_id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    code: Mapped[str] = mapped_column(String, unique=True)      # FM-qCF
    name_ru: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
