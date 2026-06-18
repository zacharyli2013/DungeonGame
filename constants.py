# =========================================
# CONSTANTS & CONFIGURATION
# =========================================

MAX_INVENTORY_SIZE = 5

# Item definitions
ITEMS = {
    "Health Potion": {
        "effect": "heal",
        "value": 0.25,
        "description": "Restore 25% of max HP"
    },
    "Sleeping Gas": {
        "effect": "sleep",
        "success_chance": 0.67,
        "actions": 2,
        "description": "67% chance: Enemy falls asleep. Player gets 2 extra actions."
    },
    "Grenade": {
        "effect": "grenade",
        "success_chance": 0.80,
        "damage_pct": 0.25,
        "description": "80% chance: Enemy loses 25% current HP. 20% chance: You lose 25% current HP."
    },
    "Golden Apple": {
        "effect": "heal",
        "value": 0.75,
        "description": "Restore 75% of max HP"
    },
    "Mysterious Key": {
        "effect": "key",
        "description": "A strange key that hums with ancient energy."
    }
}

# Weapon definitions
WEAPONS = {
    "Training Sword":  {"min_bonus": 0,  "max_bonus": 2,  "description": "+0 to +2 damage"},
    "Sturdy Axe":      {"min_bonus": 2,  "max_bonus": 4,  "description": "+2 to +4 damage"},
    "Knight's Blade":  {"min_bonus": 4,  "max_bonus": 6,  "description": "+4 to +6 damage"},
    "Magic Staff":     {"min_bonus": 3,  "max_bonus": 8,  "description": "+3 to +8 damage"},
    "Excalibur":       {"min_bonus": 15, "max_bonus": 20, "description": "+15 to +20 damage (Secret Guardian reward)"}
}

# Enemy roster
NORMAL_ENEMIES = [
    {"name": "Rat",             "hp": 8,  "str": 2, "def": 1, "gold_given": 5,  "drop_chance": 0.15},
    {"name": "Goblin",          "hp": 12, "str": 3, "def": 2, "gold_given": 10, "drop_chance": 0.20},
    {"name": "Skeleton",        "hp": 15, "str": 5, "def": 3, "gold_given": 15, "drop_chance": 0.20},
    {"name": "Orc",             "hp": 20, "str": 5, "def": 5, "gold_given": 20, "drop_chance": 0.20},
]

ELITE_ENEMIES = [
    {"name": "Goblin Captain",  "hp": 14, "str": 4,  "def": 3, "gold_given": 20, "drop_chance": 0.75},
    {"name": "Skeleton Knight", "hp": 20, "str": 5,  "def": 4, "gold_given": 30, "drop_chance": 0.75},
    {"name": "Orc Warlord",     "hp": 30, "str": 6, "def": 5, "gold_given": 40, "drop_chance": 0.75},
]

BOSS_DATA = {
    "name": "Cave King",
    "hp": 50,
    "str": 10,
    "def": 5,
    "gold_given": 500,
    "drop_chance": 1.0
}

# Merchant items per floor
MERCHANT_FLOOR_5 = [
    ("Health Potion", 5),
    ("Sleeping Gas", 10),
    ("Grenade", 10),
    ("Golden Apple", 20),
    ("Knight's Blade", 20),
]

MERCHANT_FLOOR_8 = [
    ("Health Potion", 5),
    ("Sleeping Gas", 10),
    ("Grenade", 10),
    ("Golden Apple", 20),
    ("Magic Staff", 20),
]

# Floor structure
FLOORS = [
    {"floor": 1,  "paths": ["normal"],               "description": "Tutorial Floor"},
    {"floor": 2,  "paths": ["normal", "elite"]},
    {"floor": 3,  "paths": ["normal", "rest"]},
    {"floor": 4,  "paths": ["normal", "elite"]},
    {"floor": 5,  "paths": ["normal", "merchant"]},
    {"floor": 6,  "paths": ["normal", "elite", "rest"]},
    {"floor": 7,  "paths": ["normal", "elite", "locked_door"]},
    {"floor": 8,  "paths": ["normal", "merchant", "rest"]},
    {"floor": 9,  "paths": ["normal", "elite", "locked_door"]},
    {"floor": 10, "paths": ["boss"],                 "description": "Boss Room"},
]

PATH_LABELS = {
    "normal":      "Normal Enemy",
    "elite":       "Elite Enemy",
    "rest":        "Rest Site",
    "merchant":    "Merchant",
    "locked_door": "Locked Door",
    "boss":        "Fight the Cave King"
}

POSSIBLE_DROPS = ["Health Potion", "Sleeping Gas", "Grenade", "Gold", "Weapon Upgrade"]

# Weapon upgrade tiers (for Weapon Upgrade drops)
WEAPON_TIERS = ["Sturdy Axe", "Knight's Blade", "Magic Staff"]
