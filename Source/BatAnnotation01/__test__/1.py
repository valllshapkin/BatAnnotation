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





