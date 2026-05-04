from sqlalchemy.orm import Session
from BatAnnotation.API.DataBase import seed_category
from BatAnnotation.Lookup import Species

def seed_all(db: Session):
    data = [
        # Rhinolophidae
        {"latin_name": "Rhinolophus ferrumequinum", "family": "Rhinolophidae", "genus": "Rhinolophus"},
        {"latin_name": "Rhinolophus hipposideros", "family": "Rhinolophidae", "genus": "Rhinolophus"},
        
        # Vespertilionidae (Eptesicus)
        {"latin_name": "Eptesicus serotinus", "family": "Vespertilionidae", "genus": "Eptesicus"},
        {"latin_name": "Eptesicus nilssonii", "family": "Vespertilionidae", "genus": "Eptesicus"},
        
        # Vespertilionidae (Nyctalus)
        {"latin_name": "Nyctalus noctula", "family": "Vespertilionidae", "genus": "Nyctalus"},
        {"latin_name": "Nyctalus leisleri", "family": "Vespertilionidae", "genus": "Nyctalus"},
        {"latin_name": "Nyctalus lasiopterus", "family": "Vespertilionidae", "genus": "Nyctalus"},
        
        # Vespertilionidae (Myotis)
        {"latin_name": "Myotis daubentonii", "family": "Vespertilionidae", "genus": "Myotis"},
        {"latin_name": "Myotis dasycneme", "family": "Vespertilionidae", "genus": "Myotis"},
        {"latin_name": "Myotis nattereri", "family": "Vespertilionidae", "genus": "Myotis"},
        {"latin_name": "Myotis brandtii", "family": "Vespertilionidae", "genus": "Myotis"},
        {"latin_name": "Myotis mystacinus", "family": "Vespertilionidae", "genus": "Myotis"},
        {"latin_name": "Myotis bechsteinii", "family": "Vespertilionidae", "genus": "Myotis"},
        {"latin_name": "Myotis myotis", "family": "Vespertilionidae", "genus": "Myotis"},
        {"latin_name": "Myotis blythii", "family": "Vespertilionidae", "genus": "Myotis"},
        {"latin_name": "Myotis emarginatus", "family": "Vespertilionidae", "genus": "Myotis"},
        {"latin_name": "Myotis alcathoe", "family": "Vespertilionidae", "genus": "Myotis"},
        {"latin_name": "Myotis capaccinii", "family": "Vespertilionidae", "genus": "Myotis"},
        
        # Vespertilionidae (Pipistrellus)
        {"latin_name": "Pipistrellus pipistrellus", "family": "Vespertilionidae", "genus": "Pipistrellus"},
        {"latin_name": "Pipistrellus pygmaeus", "family": "Vespertilionidae", "genus": "Pipistrellus"},
        {"latin_name": "Pipistrellus nathusii", "family": "Vespertilionidae", "genus": "Pipistrellus"},
        {"latin_name": "Pipistrellus kuhlii", "family": "Vespertilionidae", "genus": "Pipistrellus"},
        
        # Vespertilionidae (Others)
        {"latin_name": "Vespertilio murinus", "family": "Vespertilionidae", "genus": "Vespertilio"},
        {"latin_name": "Barbastella barbastellus", "family": "Vespertilionidae", "genus": "Barbastella"},
        {"latin_name": "Plecotus auritus", "family": "Vespertilionidae", "genus": "Plecotus"},
        {"latin_name": "Plecotus austriacus", "family": "Vespertilionidae", "genus": "Plecotus"},
        
        # Molossidae
        {"latin_name": "Tadarida teniotis", "family": "Molossidae", "genus": "Tadarida"},
        
        # Miniopteridae
        {"latin_name": "Miniopterus schreibersii", "family": "Miniopteridae", "genus": "Miniopterus"},
    ]
    seed_category(db, Species, "latin_name", data)
    db.commit()
