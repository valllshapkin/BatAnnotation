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