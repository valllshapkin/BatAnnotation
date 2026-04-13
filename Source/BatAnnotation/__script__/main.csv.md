

**Ты можешь создавать файлы.**
Контент файлов ты должен оборачивать в специальную маркдаун конструкцию.
``````{{ ext }} path="{{ path }}" encoding="{{ encoding }}"
{{ content }}
``````

**Внимание!**
Количество ` должно быть ровно 6.
СТРОГО СЛЕДИ за этим, так как эта конструкция парсится программно.

**Пример:**
``````py path="HelloWorld.py" encoding="utf-8"
print("Hello world!")

``````

**Пояснения к формату:**
*   `ext`: стандартный MarkDown формат (например, `py`, `html`, `css`, `js`).
*   `path`:  абсолютный или относительный путь к файлу (например, `./src/components/Button.js`).
*   `encoding`: кодировка файла.
*   `content`: **полный и готовый к использованию код** файла.

---
**КРИТИЧЕСКИ ВАЖНЫЕ ПРАВИЛА:**

1.  **ПРАВИЛО ПЕРЕНОСА СТРОКИ ПОСЛЕ БЛОКА:** После каждого закрывающего блока `````` **ВСЕГДА** должен быть как минимум один перенос строки.

2.  **ПРАВИЛО ЗАВЕРШАЮЩЕГО ПЕРЕНОСА СТРОКИ В КОНТЕНТЕ:** Содержимое (`content`) **КАЖДОГО** файла **ОБЯЗАТЕЛЬНО** должно заканчиваться как минимум одним переносом строки.

3.  **ПРАВИЛО ВЫБОРА КОДИРОВКИ (ИСПРАВЛЕНО):**
    *   Для файлов PowerShell (`.psd1`, `.psm1`) используй кодировку **`utf-16`**. Это заставит Python добавить необходимый BOM.
    *   Для файлов .ps1 используй кодировку `utf_8_sig`. Она также добавляет BOM, что является хорошей практикой для PowerShell.
    *   Для большинства других текстовых файлов (`.md`, `.json`, `.py`, `.js` и т.д.) используй кодировку `utf-8`.
---

``````text path="/MainData/Repo/golonchenroppi/BatSpecNew/Source/BatAnnotation/CommonSeeds/Core.py" encoding="utf-8"
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
``````

``````text path="/MainData/Repo/golonchenroppi/BatSpecNew/Source/BatAnnotation/CommonSeeds/EuropeGeneral.py" encoding="utf-8"
from sqlalchemy.orm import Session
from BatAnnotation.manage import seed_category
from BatAnnotation.Lookup import Species

def seed_all(db: Session):
    data = [
        # Подковоносы (Horseshoe bats)
        {"latin_name": "Rhinolophus ferrumequinum", "common_name_ru": "Большой подковонос", "common_name_en": "Greater horseshoe bat", "family": "Rhinolophidae", "genus": "Rhinolophus"},
        {"latin_name": "Rhinolophus hipposideros", "common_name_ru": "Малый подковонос", "common_name_en": "Lesser horseshoe bat", "family": "Rhinolophidae", "genus": "Rhinolophus"},
        
        # Обыкновенные кожановки и ночницы (Северная и Центральная Европа)
        {"latin_name": "Eptesicus serotinus", "common_name_ru": "Кожан поздний", "common_name_en": "Serotine", "family": "Vespertilionidae", "genus": "Eptesicus"},
        {"latin_name": "Eptesicus nilssonii", "common_name_ru": "Кожан северный", "common_name_en": "Northern bat", "family": "Vespertilionidae", "genus": "Eptesicus"},
        
        # Вечерницы (Noctule)
        {"latin_name": "Nyctalus noctula", "common_name_ru": "Вечерница рыжая", "common_name_en": "Noctule", "family": "Vespertilionidae", "genus": "Nyctalus"},
        {"latin_name": "Nyctalus leisleri", "common_name_ru": "Вечерница малая", "common_name_en": "Leisler's bat", "family": "Vespertilionidae", "genus": "Nyctalus"},
        {"latin_name": "Nyctalus lasiopterus", "common_name_ru": "Вечерница гигантская", "common_name_en": "Greater noctule", "family": "Vespertilionidae", "genus": "Nyctalus"},
        
        # Ночницы (Myotis - базовый набор)
        {"latin_name": "Myotis daubentonii", "common_name_ru": "Ночница Добантона", "common_name_en": "Daubenton's bat", "family": "Vespertilionidae", "genus": "Myotis"},
        {"latin_name": "Myotis dasycneme", "common_name_ru": "Ночница прудовая", "common_name_en": "Pond bat", "family": "Vespertilionidae", "genus": "Myotis"},
        {"latin_name": "Myotis nattereri", "common_name_ru": "Ночница Наттерера", "common_name_en": "Natterer's bat", "family": "Vespertilionidae", "genus": "Myotis"},
        {"latin_name": "Myotis brandtii", "common_name_ru": "Ночница Брандта", "common_name_en": "Brandt's bat", "family": "Vespertilionidae", "genus": "Myotis"},
        {"latin_name": "Myotis mystacinus", "common_name_ru": "Ночница усатая", "common_name_en": "Whiskered bat", "family": "Vespertilionidae", "genus": "Myotis"},
        {"latin_name": "Myotis bechsteinii", "common_name_ru": "Ночница Бехштейна", "common_name_en": "Bechstein's bat", "family": "Vespertilionidae", "genus": "Myotis"},
        {"latin_name": "Myotis myotis", "common_name_ru": "Ночница большая", "common_name_en": "Greater mouse-eared bat", "family": "Vespertilionidae", "genus": "Myotis"},
        {"latin_name": "Myotis blythii", "common_name_ru": "Ночница остроухая", "common_name_en": "Lesser mouse-eared bat", "family": "Vespertilionidae", "genus": "Myotis"},
        {"latin_name": "Myotis emarginatus", "common_name_ru": "Ночница Южная / Geoffroy's bat", "common_name_en": "Geoffroy's bat", "family": "Vespertilionidae", "genus": "Myotis"},
        {"latin_name": "Myotis alcathoe", "common_name_ru": "Ночница Алькатоэ", "common_name_en": "Alcathoe whiskered bat", "family": "Vespertilionidae", "genus": "Myotis"},
        {"latin_name": "Myotis capaccinii", "common_name_ru": "Ночница длиннопалая", "common_name_en": "Long-fingered bat", "family": "Vespertilionidae", "genus": "Myotis"},
        
        # Нетопыри (Pipistrelle)
        {"latin_name": "Pipistrellus pipistrellus", "common_name_ru": "Нетопырь-карлик", "common_name_en": "Common pipistrelle", "family": "Vespertilionidae", "genus": "Pipistrellus"},
        {"latin_name": "Pipistrellus pygmaeus", "common_name_ru": "Нетопырь-малютка", "common_name_en": "Soprano pipistrelle", "family": "Vespertilionidae", "genus": "Pipistrellus"},
        {"latin_name": "Pipistrellus nathusii", "common_name_ru": "Нетопырь Наттерера", "common_name_en": "Nathusius's pipistrelle", "family": "Vespertilionidae", "genus": "Pipistrellus"},
        {"latin_name": "Pipistrellus kuhlii", "common_name_ru": "Нетопырь Куля", "common_name_en": "Kuhl's pipistrelle", "family": "Vespertilionidae", "genus": "Pipistrellus"},
        
        # Кожанки, двухцветные и ушаны
        {"latin_name": "Vespertilio murinus", "common_name_ru": "Кожан двухцветный", "common_name_en": "Parti-coloured bat", "family": "Vespertilionidae", "genus": "Vespertilio"},
        {"latin_name": "Barbastella barbastellus", "common_name_ru": "Кожанок белополосый", "common_name_en": "Western barbastelle", "family": "Vespertilionidae", "genus": "Barbastella"},
        {"latin_name": "Plecotus auritus", "common_name_ru": "Ушан бурый", "common_name_en": "Brown long-eared bat", "family": "Vespertilionidae", "genus": "Plecotus"},
        {"latin_name": "Plecotus austriacus", "common_name_ru": "Ушан серый", "common_name_en": "Grey long-eared bat", "family": "Vespertilionidae", "genus": "Plecotus"},
        
        # Гладконосые (Free-tailed)
        {"latin_name": "Tadarida teniotis", "common_name_ru": "Гладконос европейский", "common_name_en": "European free-tailed bat", "family": "Molossidae", "genus": "Tadarida"},
        
        # Подковоносы длиннокрылые
        {"latin_name": "Miniopterus schreibersii", "common_name_ru": "Длиннокрыл обыкновенный", "common_name_en": "Schreiber's bent-winged bat", "family": "Miniopteridae", "genus": "Miniopterus"},
    ]
    seed_category(db, Species, "latin_name", data)
    db.commit()
``````

``````text path="/MainData/Repo/golonchenroppi/BatSpecNew/Source/BatAnnotation/CommonSeeds/EuropeSouthIslands.py" encoding="utf-8"
from sqlalchemy.orm import Session
from BatAnnotation.manage import seed_category
from BatAnnotation.Lookup import Species

def seed_all(db: Session):
    data = [
        # --- Средиземноморские эндемики ---
        {"latin_name": "Rhinolophus euryale", "common_name_ru": "Подковонос средиземноморский", "common_name_en": "Mediterranean horseshoe bat", "family": "Rhinolophidae", "genus": "Rhinolophus"},
        {"latin_name": "Rhinolophus mehelyi", "common_name_ru": "Подковонос Мехели", "common_name_en": "Mehely’s horseshoe bat", "family": "Rhinolophidae", "genus": "Rhinolophus"},
        {"latin_name": "Rhinolophus blasii", "common_name_ru": "Подковонос Блазия", "common_name_en": "Blasius’s horseshoe bat", "family": "Rhinolophidae", "genus": "Rhinolophus"},
        
        {"latin_name": "Eptesicus isabellinus", "common_name_ru": "Кожан меридиональный", "common_name_en": "Meridional serotine", "family": "Vespertilionidae", "genus": "Eptesicus"},
        {"latin_name": "Hypsugo savii", "common_name_ru": "Кожановидный нетопырь Сави", "common_name_en": "Savi’s pipistrelle", "family": "Vespertilionidae", "genus": "Hypsugo"},
        {"latin_name": "Plecotus kolombatovici", "common_name_ru": "Ушан средиземноморский", "common_name_en": "Mediterranean long-eared bat", "family": "Vespertilionidae", "genus": "Plecotus"},
        
        # --- Криптические и локальные виды (Пиренеи, Балканы, Кавказ) ---
        {"latin_name": "Myotis crypticus", "common_name_ru": "Ночница криптическая", "common_name_en": "Cryptic myotis", "family": "Vespertilionidae", "genus": "Myotis"},
        {"latin_name": "Myotis escalerai", "common_name_ru": "Ночница Эсклайры", "common_name_en": "Iberian Natterer’s bat", "family": "Vespertilionidae", "genus": "Myotis"},
        {"latin_name": "Myotis davidii", "common_name_ru": "Ночница Давида", "common_name_en": "David’s myotis", "family": "Vespertilionidae", "genus": "Myotis"},
        {"latin_name": "Eptesicus anatolicus", "common_name_ru": "Кожан анатолийский", "common_name_en": "Anatolian serotine", "family": "Vespertilionidae", "genus": "Eptesicus"},
        {"latin_name": "Myotis punicus", "common_name_ru": "Ночница магрибская", "common_name_en": "Maghreb mouse-eared bat", "family": "Vespertilionidae", "genus": "Myotis"},
        
        # --- Горные эндемики ---
        {"latin_name": "Plecotus macrobullaris", "common_name_ru": "Ушан альпийский", "common_name_en": "Alpine long-eared bat", "family": "Vespertilionidae", "genus": "Plecotus"},
        {"latin_name": "Hypsugo hanaki", "common_name_ru": "Нетопырь Ханака", "common_name_en": "Hanak’s pipistrelle", "family": "Vespertilionidae", "genus": "Hypsugo"},
        
        # --- Островные эндемики (Макаронезия) ---
        {"latin_name": "Nyctalus azoreum", "common_name_ru": "Вечерница азорская", "common_name_en": "Azorean noctule", "family": "Vespertilionidae", "genus": "Nyctalus"},
        {"latin_name": "Pipistrellus maderensis", "common_name_ru": "Нетопырь мадейрский", "common_name_en": "Madeira pipistrelle", "family": "Vespertilionidae", "genus": "Pipistrellus"},
        {"latin_name": "Plecotus sardus", "common_name_ru": "Ушан сардинский", "common_name_en": "Sardinian long-eared bat", "family": "Vespertilionidae", "genus": "Plecotus"},
    ]
    seed_category(db, Species, "latin_name", data)
    db.commit()
``````

``````text path="/MainData/Repo/golonchenroppi/BatSpecNew/Source/BatAnnotation/__init__.py" encoding="utf-8"
# import streamlit as st
# import numpy as np
# import matplotlib.pyplot as plt
# from matplotlib.patches import Rectangle
# import pandas as pd
# from enum import Enum
# from typing import List, Optional, Dict, Any
# from datetime import datetime
# import uuid

# # --- База данных (SQLAlchemy) ---
# from sqlalchemy import create_engine, Column, String, Float, Integer, ForeignKey, JSON, Boolean, DateTime
# from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Mapped, mapped_column

# engine = create_engine("sqlite:///:memory:")
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()


``````

``````text path="/MainData/Repo/golonchenroppi/BatSpecNew/Source/BatAnnotation/config.py" encoding="utf-8"
from typing import Type
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DEBUG = False
BASE: Type[DeclarativeBase]

def test():
    if "BASE" not in globals():
        raise ImportError(
            "BASE не инициализирован! "
            "Сначала вызовите: "
            "from BatAnnotation import config as BatAnnotationConfig; "
            "BatAnnotationConfig.BASE = ... "
            "ДО импорта моделей."
        )
    
    if not isinstance(BASE, type):
        raise ImportError("BASE должен быть классом (type)")
    
    if not issubclass(BASE, DeclarativeBase):
        raise ImportError(
            f"BASE должен быть подклассом DeclarativeBase, "
            f"а получен {BASE!r}"
        )

if DEBUG:
    print("BatAnnotation в дбаг режиме. Будет использованна тестовая BatAnnotation.config.BASE")
    
    # 1. Создаем движок (sqlite в оперативной памяти)
    # echo=True будет выводить все SQL-запросы в консоль, удобно для отладки
    engine = create_engine("sqlite:///:memory:", echo=True)
    
    # 2. Создаем фабрику сессий
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # 3. Создаем тестовый класс Base (современный стиль SQLAlchemy 2.0)
    class TestBase(DeclarativeBase):
        pass
        
    # 4. Подменяем глобальную переменную
    BASE = TestBase
``````

``````text path="/MainData/Repo/golonchenroppi/BatSpecNew/Source/BatAnnotation/Lookup.py" encoding="utf-8"
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

``````

``````text path="/MainData/Repo/golonchenroppi/BatSpecNew/Source/BatAnnotation/manage.py" encoding="utf-8"
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
``````

``````text path="/MainData/Repo/golonchenroppi/BatSpecNew/Source/BatAnnotation/REDME.md" encoding="utf-8"

# Структура базы данных (Markdown)

Ниже представлено краткое описание схемы базы данных.

## 1. Справочники (Lookup Tables)
Таблицы, содержащие фиксированные списки значений. Легко расширяются без изменения кода.

| Таблица | PK (ID) | Ключевые поля | Описание |
| :--- | :--- | :--- | :--- |
| **`ref_species`** | `species_id` | `latin_name`, `genus`, `family` | Виды летучих мышей (таксономия). |
| **`ref_detector_models`** | `detector_id` | `manufacturer`, `model`, `type` | Оборудование (Pettersson, AudioMoth и др.). |
| **`ref_habitat_types`** | `habitat_id` | `code`, `name_ru` | Тип среды (лес, водоем, город). |
| **`ref_context_types`** | `context_id` | `code`, `name_ru` | Поведение (охота, транзит, соц. зов). |
| **`ref_signal_shapes`** | `shape_id` | `code`, `name_ru` | Формы сигналов (FM, CF, qCF). |

*Примечание: Все справочники имеют поле `is_active` (Boolean) для безопасного скрытия устаревших записей.*

## 2. Основные таблицы (Трёхуровневая иерархия)

Структура данных от физического аудиофайла до конкретного акустического импульса.

### Уровень 1: `recordings` (Файл / Сессия)
Описывает сам аудиофайл и физические условия записи.
*   **PK:** `recording_id`
*   **FK:** `detector_id` -> `ref_detector_models`, `habitat_id` -> `ref_habitat_types`
*   **Поля:** `filename`, `duration_s`, `sample_rate_hz`, координаты (`lat`/`lon`), `temperature_c`.

### Уровень 2: `call_sequences` (Контекст / Пролёт)
Описывает осмысленное событие (группу писков) внутри файла. Именно здесь определяется вид летучей мыши.
*   **PK:** `sequence_id`
*   **FK:** 
    *   `recording_id` -> `recordings` (Связь с файлом)
    *   `context_id` -> `ref_context_types` (Тип поведения)
    *   `species_prediction_id` -> `ref_species` (Предсказание AI)
    *   `species_expert_id` -> `ref_species` (Оценка человека)
*   **Поля:** Глобальные рамки (`t_start_ms`, `t_end_ms`, `f_min_khz`, `f_max_khz`), `confidence` (уверенность).

### Уровень 3: `bat_calls` (Отдельный импульс / Писк)
Описывает единичный акустический сигнал внутри секвенции.
*   **PK:** `call_id`
*   **FK:** 
    *   `sequence_id` -> `call_sequences` (Связь с родительским контекстом)
    *   `shape_id` -> `ref_signal_shapes` (Форма конкретного писка)
*   **Поля:** Рамки писка (`t_start`, `t_end`, `f_min`, `f_max`), длительность (`duration_ms`), пиковая частота (`fmaxe_khz`), фичи алгоритмов (`ml_features` JSON).
``````

``````text path="/MainData/Repo/golonchenroppi/BatSpecNew/Source/BatAnnotation/Tables.py" encoding="utf-8"
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
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

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
    species_prediction_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey('ref_species.species_id'), nullable=True)
    species_expert_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey('ref_species.species_id'), nullable=True)

    t_start_ms: Mapped[float] = mapped_column(Float)
    t_end_ms: Mapped[float] = mapped_column(Float)
    f_min_khz: Mapped[float] = mapped_column(Float)
    f_max_khz: Mapped[float] = mapped_column(Float)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    # Агрегированные временные метрики секвенции
    median_ipi_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True) # Медианный интервал
    call_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)    # Количество писков

    # Relationships
    context: Mapped[Optional["ContextType"]] = relationship("ContextType")
    species_prediction: Mapped[Optional["Species"]] = relationship("Species", foreign_keys=[species_prediction_id])
    species_expert: Mapped[Optional["Species"]] = relationship("Species", foreign_keys=[species_expert_id])
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
    duration_ms: Mapped[float] = mapped_column(Float)
    fmaxe_khz: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ml_features: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Relationships
    shape: Mapped[Optional["SignalShape"]] = relationship("SignalShape")
    sequence: Mapped["CallSequence"] = relationship("CallSequence", back_populates="calls")
``````

``````text path="/MainData/Repo/golonchenroppi/BatSpecNew/Source/BatAnnotation/__test__/1.py" encoding="utf-8"
from pathlib import Path
ScriptDir = Path(__file__).parent

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

engine = create_engine(f"sqlite:///{ScriptDir.joinpath("test.db").as_posix()}", echo=False)    
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class TestBase(DeclarativeBase): pass

from BatAnnotation import config as BatAnnotationConfig
BatAnnotationConfig.BASE = TestBase

from BatAnnotation.manage import create_all; create_all(engine)

with SessionLocal() as db: 
    from BatAnnotation.CommonSeeds.Core import seed_all; seed_all(db)
    from BatAnnotation.CommonSeeds.EuropeGeneral import seed_all; seed_all(db)
    from BatAnnotation.CommonSeeds.EuropeSouthIslands import seed_all; seed_all(db)

``````

