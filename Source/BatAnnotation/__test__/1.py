from pathlib import Path; ScriptDir = Path(__file__).parent
from BatAnnotation.API.DataBase import connect, create_all

session_main, engine_main = connect(ScriptDir.joinpath("test.db"))
create_all(engine_main)

with session_main() as db: 
    from BatAnnotation.Common.Core import seed_all; seed_all(db)
    from BatAnnotation.Common.EuropeGeneral import seed_all; seed_all(db)
    from BatAnnotation.Common.EuropeSouthIslands import seed_all; seed_all(db)

print("ok")



