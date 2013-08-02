try:
    from ...achievements import achievement_functions
    give_achievement = achievement_functions.give_achievement
except ImportError:
    achievement_functions = None
    give_achievement = None

from collections import defaultdict

def check_after_move(user_id, words=[], points=0, letters_used=[]):
    if give_achievement == None: return
    
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
    if give_achievement == None: return
    return []

def check_after_game_win(user_id, games_won):
    if give_achievement == None: return
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
