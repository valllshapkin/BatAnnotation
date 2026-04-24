# = = = = = INNER = = = = = =
from BatAnnotation import config as BatAnnotationConfig
BatAnnotationConfig.test()
# = = = = = INNER = = = = = =

from typing import List, Optional, Dict, Any
from datetime import UTC, datetime
import uuid

from sqlalchemy import String, Float, Integer, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column

from BatAnnotation.Lookup import ContextType, DetectorModel, HabitatType, SignalShape, Species

# ==============================================================================
# ОСНОВНЫЕ ТАБЛИЦЫ — ссылаются на справочники через FK
# ==============================================================================

class Recording(BatAnnotationConfig.BASE):
    __tablename__ = 'recordings'

    recording_id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename: Mapped[str] = mapped_column(String)
    duration_s: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sample_rate_hz: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # FK на справочники
    detector_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey('ref_detector_models.detector_id'), nullable=True)
    habitat_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey('ref_habitat_types.habitat_id'), nullable=True)

    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    altitude_m: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    recorded_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    temperature_c: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Relationships
    detector: Mapped[Optional["DetectorModel"]] = relationship("DetectorModel")
    habitat: Mapped[Optional["HabitatType"]] = relationship("HabitatType")
    sequences: Mapped[List["CallSequence"]] = relationship("CallSequence", back_populates="recording", cascade="all, delete-orphan")


class CallSequence(BatAnnotationConfig.BASE):
    __tablename__ = 'call_sequences'

    sequence_id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    recording_id: Mapped[str] = mapped_column(String, ForeignKey('recordings.recording_id'), index=True)

    # FK на справочники
    context_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey('ref_context_types.context_id'), nullable=True)
    species_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey('ref_species.species_id'), nullable=True)

    t_start_ms: Mapped[float] = mapped_column(Float)
    t_end_ms: Mapped[float] = mapped_column(Float)
    f_min_khz: Mapped[float] = mapped_column(Float)
    f_max_khz: Mapped[float] = mapped_column(Float)
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Relationships
    context: Mapped[Optional["ContextType"]] = relationship("ContextType")
    species: Mapped[Optional["Species"]] = relationship("Species")
    recording: Mapped["Recording"] = relationship("Recording", back_populates="sequences")
    calls: Mapped[List["BatCall"]] = relationship("BatCall", back_populates="sequence", cascade="all, delete-orphan")


class BatCall(BatAnnotationConfig.BASE):
    __tablename__ = 'bat_calls'

    call_id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    sequence_id: Mapped[str] = mapped_column(String, ForeignKey('call_sequences.sequence_id'), index=True)

    # FK на справочник
    shape_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey('ref_signal_shapes.shape_id'), nullable=True)

    t_start_ms: Mapped[float] = mapped_column(Float)
    t_end_ms: Mapped[float] = mapped_column(Float)
    f_min_khz: Mapped[float] = mapped_column(Float)
    f_max_khz: Mapped[float] = mapped_column(Float)
    
    fmaxe_khz: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    t_fmaxe_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    signal_curves: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Relationships
    shape: Mapped[Optional["SignalShape"]] = relationship("SignalShape")
    sequence: Mapped["CallSequence"] = relationship("CallSequence", back_populates="calls")
