from ...achievements import achievement_functions
from collections import defaultdict

give_achievement = achievement_functions.give_achievement

# Register achievements
achievements = (
    ("wordy_bingo", "Bingo!", "Use all your letters in one go", 5, 1),
    ("wordy_5_letter", "Pentuplite", "Score using 20 five letter words", 5, 20),
    ("wordy_6_letter", "Sextuplite", "Score using 10 six letter words", 10, 10),
    ("wordy_7_letter", "Septuplite", "Score using 8 seven letter words", 15, 8),
    ("wordy_8_letter", "Octuplite", "Score using 5 eight letter words", 20, 5),
    ("wordy_9_letter", "Nontuplite", "Score using 3 nine letter words", 25, 3),
    ("wordy_10_letter", "Dectuplite", "Score using a ten letter word", 30, 1),
    ("wordy_start_and_end", "Start with the end", "Having a word start and end with the same letter", 10, 5),
    
    ("wordy_100_tiles", "Well spoken", "Place a total of 100 tiles", 5, 100),
    ("wordy_500_tiles", "Eloquent", "Place a total of 500 tiles", 10, 500),
    ("wordy_1000_tiles", "Sesquipedalian", "Place a total of 1000 tiles", 20, 1000),
    
    ("wordy_50_pointer", "50 points", "Score 50+ points with one move", 5, 1),
    ("wordy_75_pointer", "75 points", "Score 75+ points with one move", 10, 1),
    ("wordy_100_pointer", "100 points", "Score 100+ points with one move", 15, 1),
    ("wordy_125_pointer", "125 points", "Score 125+ points with one move", 20, 1),
    ("wordy_150_pointer", "150 points", "Score 150+ points with one move", 25, 1),
    
    ("wordy_win_5_games", "Five time champion", "Win 5 games of wordy", 5, 5),
    ("wordy_win_10_games", "Ten time champion", "Win 10 games of wordy", 10, 10),
    ("wordy_win_15_games", "Fifteen time champion", "Win 15 games of wordy", 15, 15),
    ("wordy_win_25_games", "Twentyfive time champion", "Win 25 games of wordy", 20, 25),
    ("wordy_dominant", "Dominance", "Defeat the same opponent 10 times", 20, 1),
)

# Set up the groupings
achievement_functions.sections['Wordy'] = {
    "name":"Wordy",
    "sub_categories": {
        "GargantuanWords": {
            "name": "Gargantuan Words",
            "achievements": ("wordy_bingo", "wordy_5_letter", "wordy_6_letter", "wordy_7_letter", "wordy_8_letter", "wordy_9_letter", "wordy_10_letter", "wordy_start_and_end"),
        },
        "MultitudinousTiles": {
            "name": "Multitudinous Tiles",
            "achievements": ("wordy_100_tiles", "wordy_500_tiles", "wordy_1000_tiles"),
        },
        "MonumentalScores": {
            "name": "Monumental Scores",
            "achievements": ("wordy_50_pointer", "wordy_75_pointer", "wordy_100_pointer", "wordy_125_pointer", "wordy_150_pointer"),
        },
        "MyriadVictories": {
            "name": "Myriadic Victories",
            "achievements": ("wordy_win_5_games", "wordy_win_10_games", "wordy_win_15_games", "wordy_win_25_games", "wordy_dominant"),
        }
    }
}

def check_after_move(user_id, words=[], points=0, letters_used=[]):
    achieved = []
    
    for w in words:
        if len(w) == 5: achieved.append(give_achievement("wordy_5_letter", user_id))
        if len(w) == 6: achieved.append(give_achievement("wordy_6_letter", user_id))
        if len(w) == 7: achieved.append(give_achievement("wordy_7_letter", user_id))
        if len(w) == 8: achieved.append(give_achievement("wordy_8_letter", user_id))
        if len(w) == 9: achieved.append(give_achievement("wordy_9_letter", user_id))
        if len(w) == 10: achieved.append(give_achievement("wordy_10_letter", user_id))
        
        if w[0] == w[-1]: achieved.append(give_achievement("wordy_start_and_end", user_id))
    
    if len(letters_used) == 7:
        achieved.append(give_achievement("wordy_bingo", user_id))
    
    achieved.append(give_achievement("wordy_start_and_end", user_id))
    achieved.append(give_achievement("wordy_100_tiles", user_id, acount=len(letters_used)))
    achieved.append(give_achievement("wordy_500_tiles", user_id, acount=len(letters_used)))
    achieved.append(give_achievement("wordy_1000_tiles", user_id, acount=len(letters_used)))
    
    if points >= 50: achieved.append(give_achievement("wordy_50_pointer", user_id))
    if points >= 75: achieved.append(give_achievement("wordy_75_pointer", user_id))
    if points >= 100: achieved.append(give_achievement("wordy_100_pointer", user_id))
    if points >= 125: achieved.append(give_achievement("wordy_125_pointer", user_id))
    if points >= 150: achieved.append(give_achievement("wordy_150_pointer", user_id))
    
    return achieved

def check_after_game_end(user_id, the_game):
    return []

def check_after_game_win(user_id, games_won):
    achieved = []
    
    achieved.append(give_achievement("wordy_win_5_games", user_id))
    achieved.append(give_achievement("wordy_win_10_games", user_id))
    achieved.append(give_achievement("wordy_win_15_games", user_id))
    achieved.append(give_achievement("wordy_win_25_games", user_id))
    
    domination_count = defaultdict(int)
    for g in games_won:
        for p in g.players:
            domination_count[p] += 1
        
    del(domination_count[p])
    for k, v in domination_count.items():
        if v >= 10:
            achieved.append(give_achievement("wordy_dominant", user_id))
    
    return achieved
