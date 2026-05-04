from sqlalchemy.orm import Session
from BatAnnotation.API.DataBase import seed_category
from BatAnnotation.Lookup import Species

def seed_all(db: Session):
    data = [
        # Mediterranean endemics
        {"latin_name": "Rhinolophus euryale", "family": "Rhinolophidae", "genus": "Rhinolophus"},
        {"latin_name": "Rhinolophus mehelyi", "family": "Rhinolophidae", "genus": "Rhinolophus"},
        {"latin_name": "Rhinolophus blasii", "family": "Rhinolophidae", "genus": "Rhinolophus"},
        
        {"latin_name": "Eptesicus isabellinus", "family": "Vespertilionidae", "genus": "Eptesicus"},
        {"latin_name": "Hypsugo savii", "family": "Vespertilionidae", "genus": "Hypsugo"},
        {"latin_name": "Plecotus kolombatovici", "family": "Vespertilionidae", "genus": "Plecotus"},
        
        # Cryptic & Local (Pyrenees, Balkans, Caucasus)
        {"latin_name": "Myotis crypticus", "family": "Vespertilionidae", "genus": "Myotis"},
        {"latin_name": "Myotis escalerai", "family": "Vespertilionidae", "genus": "Myotis"},
        {"latin_name": "Myotis davidii", "family": "Vespertilionidae", "genus": "Myotis"},
        {"latin_name": "Eptesicus anatolicus", "family": "Vespertilionidae", "genus": "Eptesicus"},
        {"latin_name": "Myotis punicus", "family": "Vespertilionidae", "genus": "Myotis"},
        
        # Mountain endemics
        {"latin_name": "Plecotus macrobullaris", "family": "Vespertilionidae", "genus": "Plecotus"},
        {"latin_name": "Hypsugo hanaki", "family": "Vespertilionidae", "genus": "Hypsugo"},
        
        # Island endemics (Macaronesia)
        {"latin_name": "Nyctalus azoreum", "family": "Vespertilionidae", "genus": "Nyctalus"},
        {"latin_name": "Pipistrellus maderensis", "family": "Vespertilionidae", "genus": "Pipistrellus"},
        {"latin_name": "Plecotus sardus", "family": "Vespertilionidae", "genus": "Plecotus"},
    ]
    seed_category(db, Species, "latin_name", data)
    db.commit()
