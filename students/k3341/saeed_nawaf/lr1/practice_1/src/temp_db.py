professions = {
    1: {"id": 1, "title": "Warrior", "description": "A strong fighter"},
    2: {"id": 2, "title": "Mage", "description": "A powerful spellcaster"},
    3: {"id": 3, "title": "Archer", "description": "A precise ranged attacker"},
}

skills = {
    1: {"id": 1, "name": "Swordsmanship", "description": "Master of swords"},
    2: {"id": 2, "name": "Magic Shield", "description": "Creates a protective barrier"},
    3: {"id": 3, "name": "Archery", "description": "Expert bow skills"},
}

warriors = {
    1: {"id": 1, "race": "Human", "name": "Arthur", "level": 10, "profession_id": 1, "skill_ids": [1, 2]},
    2: {"id": 2, "race": "Elf", "name": "Legolas", "level": 15, "profession_id": 3, "skill_ids": [3]},
    3: {"id": 3, "race": "Dwarf", "name": "Gimli", "level": 12, "profession_id": 1, "skill_ids": [1]},
}

counter = {"value": 4}
profession_counter = {"value": 4}
skill_counter = {"value": 4}
