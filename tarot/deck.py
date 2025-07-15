# import datetime

# SUITS = ["Cups", "Swords", "Wands", "Pentacles"]
# NUMBERS = ["Two", "Three", "Four", "Five", "Six", "Sezeven", "Eight", "Nine", "Ten"]
# NUMERIC_CARDS = [f"{n} of {s}" for s in SUITS for n in NUMBERS]  # 36 cards
# COURT_RANKS = ["Page", "Knight", "Queen", "King"]
# COURT_CARDS = [f"{r} of {s}" for s in SUITS for r in COURT_RANKS]  # 16 cards
# MAJOR_ARCANA = [
# "The Fool", "The Magician", "The High Priestess", "The Empress",
# "The Emperor", "The Hierophant", "The Lovers", "The Chariot",
# "Strength", "The Hermit", "Wheel of Fortune", "Justice",
# "The Hanged Man", "Death", "Temperance", "The Devil",
# "The Tower", "The Star", "The Moon", "The Sun",
# "Judgement", "The World"
# ]  # 22 cards

# FULL_DECK = MAJOR_ARCANA + NUMERIC_CARDS + COURT_CARDS  # total 78
# NEGATIVE_CARDS = [
# "The Tower", "Five of Cups", "Three of Swords", "Ten of Swords"
# ]
# POLARITY = {card: ("negative" if card in NEGATIVE_CARDS else "positive") for card in FULL_DECK}

# DATE_RANGES = {}
# year = datetime.date.today().year
# start_date = datetime.date(year, 1, 1)
# for idx, card in enumerate(NUMERIC_CARDS):
#     dr_start = start_date + datetime.timedelta(days=idx * 10)
#     dr_end = dr_start + datetime.timedelta(days=9)
#     DATE_RANGES[card] = (dr_start, dr_end)

import datetime

SUITS = ["Cups", "Swords", "Wands", "Pentacles"]
NUMBERS = ["Ace", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten"]
COURTS = ["Page", "Knight", "Queen", "King"]

MINOR_ARCANA = [f"{num} of {suit}" for suit in SUITS for num in NUMBERS + COURTS]

MAJOR_ARCANA = [
     "The Fool", "The Magician", "The High Priestess", "The Empress", "The Emperor", "The Hierophant",
    "The Lovers", "The Chariot", "Strength", "The Hermit", "Wheel of Fortune", "Justice", "The Hanged Man",
    "Death", "Temperance", "The Devil", "The Tower", "The Star", "The Moon", "The Sun", "Judgement", "The World",
    "Ace of Wands", "Two of Wands", "Three of Wands", "Four of Wands", "Five of Wands", "Six of Wands", 
    "Seven of Wands", "Eight of Wands", "Nine of Wands", "Ten of Wands", "Page of Wands", "Knight of Wands",
    "Queen of Wands", "King of Wands",
    "Ace of Cups", "Two of Cups", "Three of Cups", "Four of Cups", "Five of Cups", "Six of Cups", 
    "Seven of Cups", "Eight of Cups", "Nine of Cups", "Ten of Cups", "Page of Cups", "Knight of Cups",
    "Queen of Cups", "King of Cups",
    "Ace of Swords", "Two of Swords", "Three of Swords", "Four of Swords", "Five of Swords", "Six of Swords", 
    "Seven of Swords", "Eight of Swords", "Nine of Swords", "Ten of Swords", "Page of Swords", "Knight of Swords",
    "Queen of Swords", "King of Swords",
    "Ace of Pentacles", "Two of Pentacles", "Three of Pentacles", "Four of Pentacles", "Five of Pentacles",
    "Six of Pentacles", "Seven of Pentacles", "Eight of Pentacles", "Nine of Pentacles", "Ten of Pentacles",
    "Page of Pentacles", "Knight of Pentacles", "Queen of Pentacles", "King of Pentacles"
]

FULL_DECK = MINOR_ARCANA + MAJOR_ARCANA

# Numeric cards for timing
NUMERIC_CARDS = [f"{num} of {suit}" for suit in SUITS for num in NUMBERS[1:]]

def generate_date_ranges():
    ranges = {}
    year_start = datetime.date(datetime.date.today().year, 1, 1)
    for i, card in enumerate(NUMERIC_CARDS):
        start = year_start + datetime.timedelta(days=i*10)
        end = start + datetime.timedelta(days=9)
        ranges[card] = (start, end)
    return ranges

DATE_RANGES = generate_date_ranges()
#whenprint(DATE_RANGES)