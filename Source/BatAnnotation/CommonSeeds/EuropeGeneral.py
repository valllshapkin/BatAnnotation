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