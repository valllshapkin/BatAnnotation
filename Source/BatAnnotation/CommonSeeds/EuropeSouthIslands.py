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