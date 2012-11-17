from .achievement_functions import give_achievement
from collections import defaultdict

# Register achievements
achievements = (
    ("wordy_bingo", "Bingo!", "Use all your letters in one go", 5, 5),
    ("wordy_5_letter", "5 letter word", "5 letter word", 5, 20),
    ("wordy_6_letter", "6 letter word", "6 letter word", 10, 10),
    ("wordy_7_letter", "7 letter word", "7 letter word", 15, 8),
    ("wordy_8_letter", "8 letter word", "8 letter word", 20, 5),
    ("wordy_9_letter", "9 letter word", "9 letter word", 25, 3),
    ("wordy_10_letter", "10 letter word", "10 letter word", 30, 1),
    
    ("wordy_start_and_end", "Start and end with the same letter", "Having a word start and end with the same letter", 10, 5),
    ("wordy_100_tiles", "Well spoken", "Place a total of 100 tiles", 5, 100),
    ("wordy_500_tiles", "Eloquent", "Place a total of 500 tiles", 10, 500),
    ("wordy_1000_tiles", "Sesquipedalian", "Place a total of 1000 tiles", 20, 1000),
    
    ("wordy_50_pointer", "50 points", "Score 50 points with one move", 5, 1),
    ("wordy_75_pointer", "75 points", "Score 75 points with one move", 10, 1),
    ("wordy_100_pointer", "100 points", "Score 100 points with one move", 15, 1),
    ("wordy_125_pointer", "125 points", "Score 125 points with one move", 20, 1),
    ("wordy_150_pointer", "150 points", "Score 150 points with one move", 25, 1),
    
    ("wordy_win_5_games", "Five time champion", "Win 5 games of wordy", 5, 5),
    ("wordy_win_10_games", "Ten time champion", "Win 10 games of wordy", 10, 5),
    ("wordy_win_15_games", "Fifteen time champion", "Win 15 games of wordy", 15, 5),
    ("wordy_win_25_games", "Twentyfive time champion", "Win 25 games of wordy", 20, 5),
    ("wordy_dominant", "Dominance", "Defeat the same opponent 10 times", 20, 1),
)

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
