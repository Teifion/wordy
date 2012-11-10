import random
import re
from collections import defaultdict

# http://en.wikipedia.org/w/index.php?title=File:Blank_Scrabble_board_with_coordinates.svg&page=1
# Double/Triple word scores
dws = (
    (1,1),              (13,1),
      (2,2),          (12,2),
        (3,3),      (11,3),
          (4,4),  (10,4),
        
          (4,10), (10,10),
        (3,11),     (11,11),
      (2,12),         (12,12),
    (1,13),             (13,13),
)
tws = (
    (0,0),  (7,0),  (14,0),
    (0,7),          (14,7),
    (0,14), (7,14), (14,14)
)

# Double/Triple letter scores
dls = (
          (3,0),                  (11,0),
                  (6,2),  (8,2),
    (0,3),            (7,3),              (14,3),
    
        (2,6),    (6,6),  (8,6),    (12,6),
          (3,7),                  (11,7),
        (2,8),    (6,8),  (8,8),    (12,8),
       
    (0,11),           (7,11),             (14,11),
                  (6,12), (8,12),
          (3,14),                  (11,14),
)
tls = (
            (5,1),      (9,1),
    
    (1,5),  (5,5),      (9,5),   (13,5),
    
    (1,9),  (5,9),      (9,9),   (13,9),
    
            (5,13),     (9,13),
)

# ABCDEFGHIJKLMNO
# 0123456789ABCDE

default_bag = "EEEEEEEEEEEEAAAAAAAAAIIIIIIIIIOOOOOOOONNNNNNRRRRRRTTTTTTLLLLSSSSUUUUDDDDGGGBBCCMMPPFFHHVVWWYYKJXQZ**"
default_bag = "EEEEEEEEEEEEAAAAAAAAAIIIIIIIIIOOOOOOOONNNNNNRRRRRRTTTTTTLLLLSSSSUUUUDDDDGGGBBCCMMPPFFHHVVWWYYKJXQZ"

testing_board = """
ABCDEFGHIJKLMNO
PQRSTUVWXYZ____
_______________
_______________
_______________
_______________
_______________
_______________
_______________
_______________
_______________
_______________
_______________
_______________
_______________
""".replace("\n","").replace("_"," ").strip()

"ABCDEFGHIJKLMNOPQRSTUVWXYZ                                                                                                                                                                                                       "

dummy_board = """
___Q___G_______
___U_P_A_______
CEDI_A_I_______
___NORITE______
_____L____Y____
____BEAU_DOS__Y
____O_____G___O
A___T_SIZIER__R
V__WHEW___E_ORE
A__I_MU_____N__
SHUN__MIGRATE__
T__E___V_____B_
_____DJINN___U_
_______E_O___L_
____FOPS_D_TALC
""".replace("\n","").replace("_"," ").strip()

"   Q   G          U P A       CEDI A I          NORITE           L    Y        BEAU DOS  Y    O     G   OA   T SIZIER  RV  WHEW   E OREA  I MU     N  SHUN  MIGRATE  T  E   V     B      DJINN   U        E O   L     FOPS D TALC"

# http://en.wikipedia.org/wiki/Scrabble_letter_distributions
# 2 blank tiles (scoring 0 points)
# 1 point: E ×12, A ×9, I ×9, O ×8, N ×6, R ×6, T ×6, L ×4, S ×4, U ×4
# 2 points: D ×4, G ×3
# 3 points: B ×2, C ×2, M ×2, P ×2
# 4 points: F ×2, H ×2, V ×2, W ×2, Y ×2
# 5 points: K ×1
# 8 points: J ×1, X ×1
# 10 points: Q ×1, Z ×1

letter_values = {
    "A": 1,
    "B": 3,
    "C": 3,
    "D": 2,
    "E": 1,
    "F": 4,
    "G": 2,
    "H": 4,
    "I": 1,
    "J": 8,
    "K": 5,
    "L": 1,
    "M": 3,
    "N": 1,
    "O": 1,
    "P": 3,
    "Q": 10,
    "R": 1,
    "S": 1,
    "T": 1,
    "U": 1,
    "V": 4,
    "W": 4,
    "X": 8,
    "Y": 4,
    "Z": 10,
    "*": 0,
    " ": 0,
    "_": 0,
}

def _pp_board(the_board):
    if type(the_board) == str:
        the_board = string_to_board(the_board)
    
    print("\n")
    print(" %s " % ("-" * 15))
    for r in the_board:
        print("|%s|" % "".join(r))
    print(" %s " % ("-" * 15))
    print("\n")

def string_to_board(board_string):
    the_board = []
    
    for r in range(15):
        a = r * 15
        b = r * 15 + 15
        the_board.append(list(board_string[a:b]))
    
    return the_board

def board_to_string(board_lists):
    return "".join(["".join(b) for b in board_lists])

def pick_from_bag(the_bag, tiles=7):
    if type(the_bag) == str:
        new_bag = list(the_bag)
    else:
        new_bag = list(the_bag)
    
    letters = []
    
    while len(letters) < tiles and len(new_bag) > 0:
        r = random.randint(0, len(new_bag)-1)
        letters.append(new_bag.pop(r))
    
    return "".join(letters), "".join(new_bag)

def player_turn(turn_number, players = 2):
    return 1 + (turn_number % players)

def perform_move(the_game, player_id, new_letters):
    return attempt_move(the_game, player_id, new_letters, perform=True)

def attempt_move(the_game, player_id, new_letters, perform=False):
    # Whose turn is it anyways?
    p_turn = player_turn(the_game.turn)
    not_your_turn = False
    if p_turn == 1:
        player_letters = the_game.player1_tiles
        if the_game.player1 != player_id: not_your_turn = True
    elif p_turn == 2:
        player_letters = the_game.player2_tiles
        if the_game.player2 != player_id: not_your_turn = True
    elif p_turn == 3:
        player_letters = the_game.player3_tiles
        if the_game.player3 != player_id: not_your_turn = True
    elif p_turn == 4:
        player_letters = the_game.player4_tiles
        if the_game.player4 != player_id: not_your_turn = True
    
    if not_your_turn:
        raise Exception("It is not your turn yet")
    
    # Get the board as a string
    b = string_to_board(the_game.board)
    
    # We want to make sure all the letters can be placed in these locations
    xs, ys = set(), set()
    for l, x, y in new_letters:
        if x < 0 or x > 14 or y < 0 or y > 14:
            raise KeyError("{},{} is not a valid tile (15x15 board size)".format(x, y))
       
        if b[y][x] != " ":
            raise KeyError("{},{} is already occupied by a letter".format(x, y))
       
        # b[y][x] = l
       
        xs.add(x)
        ys.add(y)
    
    if len(xs) > 1 and len(ys) > 1:
        raise KeyError("You must place all your tiles in one row or one column")
       
    # Now make sure they're placing the tiles next to existing tiles
    # At least one tiles needs to be non-diagonally next to another
    is_next_to_a_tile = False
    for l, x, y in new_letters:
        if is_next_to_a_tile: continue
       
        # X
        if x > 0 and b[y][x-1] != " ": is_next_to_a_tile = True
        if x < 14 and b[y][x+1] != " ": is_next_to_a_tile = True
       
        # Y
        if y > 0 and b[y-1][x] != " ": is_next_to_a_tile = True
        if y < 14 and b[y+1][x] != " ": is_next_to_a_tile = True
    
    if not is_next_to_a_tile and the_game.turn > 0:
        raise KeyError("You must place your tiles next to existing tiles")
    
    # Add letters to the board
    for l, x, y in new_letters:
        b[y][x] = l
    
    # Next we want to make sure there are no gaps between our tiles
    if len(xs) > 1:
        minx, maxx = min(xs), max(xs)
        y = list(ys)[0]
       
        for x in range(minx, maxx):
            if b[y][x] == " ":
                raise KeyError("Your tiles must all be part of the same word (no gaps allowed)")
       
    if len(ys) > 1:
        miny, maxy = min(ys), max(ys)
        x = list(xs)[0]
       
        for y in range(miny, maxy):
            if b[y][x] == " ":
                raise KeyError("Your tiles must all be part of the same word (no gaps allowed)")
    
    # If it's turn 0 then we need to make sure the centre is covered
    if b[7][7] == " ":
        raise KeyError("The centre tile is not covered")
    
    # Now we want to find all the words to check in the datbase
    points = 0
    words = []
    covered = set()
    for l, x, y in new_letters:
        if (x,y) in covered: continue
       
        # Go left until we hit an empty space or edge of the board
        temp_x = x
        temp_l = l
        while temp_x >= 0 and temp_l != " ":
            temp_l = b[y][temp_x]
            temp_x -= 1
       
        temp_x += 1
        if temp_l == " ": temp_x += 1
        temp_l = ""
       
        # Read right until the same, this is one word
        new_word = []
        word_points = 0
        word_multiplier = 1
        while temp_x <= 14 and temp_l != " ":
            covered.add((temp_x, y))
            temp_l = b[y][temp_x]
            new_word.append(temp_l)
           
            letter_multiplier = 1
           
            # If it's fresh we check for special tiles
            if (temp_l, temp_x, y) in new_letters:
                if (temp_x, y) in dws: word_multiplier *= 2
                if (temp_x, y) in tws: word_multiplier *= 3
               
                if (temp_x, y) in dls: letter_multiplier = 2
                if (temp_x, y) in tls: letter_multiplier = 3
           
            word_points += (letter_values[temp_l] * letter_multiplier)
            temp_x += 1
       
        new_word = "".join(new_word).strip()
        if len(new_word) > 1:
            points += (word_points * word_multiplier)
            words.append(new_word)
    
    # Repeat for Y
    # We don't put them in the same loop as it's not easy to track which tiles we've already covered
    covered = set()
    for l, x, y in new_letters:
        if (x,y) in covered: continue
       
        # Go left until we hit an empty space or edge of the board
        temp_y = y
        temp_l = l
        while temp_y >= 0 and temp_l != " ":
            temp_l = b[temp_y][x]
            temp_y -= 1
       
        temp_y += 1
        if temp_l == " ": temp_y += 1
        temp_l = ""
       
        # Read right until the same, this is one word
        new_word = []
        word_points = 0
        word_multiplier = 1
        while temp_y <= 14 and temp_l != " ":
            covered.add((x, temp_y))
            temp_l = b[temp_y][x]
            new_word.append(temp_l)
           
            letter_multiplier = 1
           
            # If it's fresh we check for special tiles
            if (temp_l, x, temp_y) in new_letters:
                if (x, temp_y) in dws: word_multiplier *= 2
                if (x, temp_y) in tws: word_multiplier *= 3
               
                if (x, temp_y) in dls: letter_multiplier = 2
                if (x, temp_y) in tls: letter_multiplier = 3
           
            word_points += (letter_values[temp_l] * letter_multiplier)
            temp_y += 1
       
        new_word = "".join(new_word).strip()
        if len(new_word) > 1:
            points += (word_points * word_multiplier)
            words.append(new_word)
    
    # If we're not performing then we will just return the points and assume they are valid words
    if not perform:
        return points
    
    # Get a list of these words from the database
    # any word not in the list we get back is an invalid word
    db_words = get_words_from_db(words)
    
    invalid = []
    for w in words:
        if w not in db_words:
            invalid.append(w)
    
    if invalid != []:
        if len(invalid) == 1:
            raise KeyError("{} is not a valid word".format(invalid[0]))
        else:
            raise KeyError("{} and {} are not valid words".format(", ".join(invalid[:-1]), invalid[-1]))
    
    # At this stage it's been a success, we need to update the board and player tiles
    new_tiles, new_bag = pick_from_bag(the_game.game_bag, tiles=len(new_letters))
    
    for l, x, y in new_letters:
        player_letters = player_letters.replace(l, "", 1)
    
    the_game.board = board_to_string(b)
    the_game.turn += 1
    the_game.game_bag = new_bag
    
    if p_turn == 1:
        the_game.player1_tiles = player_letters + new_tiles
        player_name = get_player_name(the_game.player1)
    elif p_turn == 2:
        the_game.player2_tiles = player_letters + new_tiles
        player_name = get_player_name(the_game.player2)
    elif p_turn == 3:
        the_game.player3_tiles = player_letters + new_tiles
        player_name = get_player_name(the_game.player3)
    elif p_turn == 4:
        the_game.player4_tiles = player_letters + new_tiles
        player_name = get_player_name(the_game.player4)
    
    # Build a description of the words
    words = [w.title() for w in words]
    if len(words) == 1:
        word_string = words[0]
    else:
        word_string = "{} and {}".format(", ".join(words[:-1]), words[-1])
    
    the_game.turn_log += "\n{player_name}: {the_word} for {points} points".format(
        player_name = player_name,
        the_word = word_string,
        points = points,
    )
    the_game.turn_log = the_game.turn_log.strip()
    
    # They may just want to know how many points this will score
    if len(new_letters) == 7:
        points += 50
    
    # Do we need to end the game?
    if scan_for_end(the_game):
        player_1_name = get_player_name(the_game.player1)
        player_2_name = get_player_name(the_game.player2)
       
        scores = tally_scores(the_game)
       
        scores[player_1_name] = scores.get(player_1_name, 0) + scores[2]
        scores[player_2_name] = scores.get(player_2_name, 0) + scores[1]
       
        if scores[player_1_name] > scores[player_2_name]:
            the_game.winner = the_game.player1
            the_game.turn_log += "\n\nAfter counting tiles, {} has won the game {} points to {}".format(
                player_1_name,
                scores.get(player_1_name, 0),
                scores.get(player_2_name, 0)
            )
            
        elif scores[player_1_name] < scores[player_2_name]:
            the_game.winner = the_game.player2
            the_game.turn_log += "\n\nAfter counting tiles, {} has won the game {} points to {}".format(
                player_2_name,
                scores.get(player_2_name, 0),
                scores.get(player_1_name, 0)
            )
           
        else:
            # Draw
            the_game.winner = -1
            the_game.turn_log += "\n\nAfter counting tiles, the game has ended in a draw"
    
    update_game(the_game)
    return "{} points".format(points)

def scan_for_end(the_game):
    if the_game.game_bag == "":
        if the_game.player1_tiles == "" or the_game.player2_tiles == "":
            return True
    
    return False

def forfeit_game(the_game, user_id):
    if the_game.player1 == user_id:
        the_game.winner = the_game.player2
        the_game.turn_log += "\nForfeit by {}\nVictory for {}".format(
            get_player_name(the_game.player1),
            get_player_name(the_game.player2),
        )
    elif the_game.player2 == user_id:
        the_game.winner = the_game.player1
        the_game.turn_log += "\nForfeit by {}\nVictory for {}".format(
            get_player_name(the_game.player2),
            get_player_name(the_game.player1),
        )

def swap_letters(the_game, user_id):
    p_turn = player_turn(the_game.turn)
    
    if the_game.player1 == user_id and p_turn == 1:
        full_bag = the_game.game_bag + the_game.player1_tiles
        the_game.player1_tiles, the_game.game_bag = pick_from_bag(full_bag, tiles=7)
    elif the_game.player2 == user_id and p_turn == 2:
        full_bag = the_game.game_bag + the_game.player2_tiles
        the_game.player2_tiles, the_game.game_bag = pick_from_bag(full_bag, tiles=7)
    else:
        return
    
    the_game.turn_log += "\n{player_name} swapped their tiles".format(
        player_name = get_player_name(user_id),
    )
    the_game.turn_log = the_game.turn_log.strip()
    the_game.turn += 1
    update_game(the_game)

pass_turn_search = re.compile(r"^.* passed on their turn$")
def pass_turn(the_game, user_id):
    p_turn = player_turn(the_game.turn)
    
    if the_game.player1 == user_id and p_turn == 1:
        pass
    elif the_game.player2 == user_id and p_turn == 2:
        pass
    else:
        return
    
    last_log = the_game.turn_log.split("\n")[-1]
    if pass_turn_search.search(last_log):
        the_game.winner = -1
        the_game.turn_log += "\n{player_name} passed on their turn".format(
            player_name = get_player_name(user_id),
        )
        
        # Now end the game
        the_game.turn_log += "\nAs both players have ended passed on their turn, the game is ended".format(
            player_name = get_player_name(user_id),
        )
        player_1_name = get_player_name(the_game.player1)
        player_2_name = get_player_name(the_game.player2)
       
        scores = tally_scores(the_game)
       
        scores[player_1_name] = scores.get(player_1_name, 0) + scores[2]
        scores[player_2_name] = scores.get(player_2_name, 0) + scores[1]
       
        if scores[player_1_name] > scores[player_2_name]:
            the_game.winner = the_game.player1
            the_game.turn_log += "\n\nAfter counting tiles, {} has won the game {} points to {}".format(
                player_1_name,
                scores.get(player_1_name, 0),
                scores.get(player_2_name, 0)
            )
            
        elif scores[player_1_name] < scores[player_2_name]:
            the_game.winner = the_game.player2
            the_game.turn_log += "\n\nAfter counting tiles, {} has won the game {} points to {}".format(
                player_2_name,
                scores.get(player_2_name, 0),
                scores.get(player_1_name, 0)
            )
           
        else:
            # Draw
            the_game.winner = -1
            the_game.turn_log += "\n\nAfter counting tiles, the game has ended in a draw"
        
        update_game(the_game)
        
    else:
        the_game.turn_log += "\n{player_name} passed on their turn".format(
            player_name = get_player_name(user_id),
        )
        the_game.turn_log = the_game.turn_log.strip()
        the_game.turn += 1
        update_game(the_game)


# This is a function you might need to alter to get at the words from the database
from ...models import (
    DBSession,
    User,
    WordyWord,
)

def get_words_from_db(words):
    return [w[0] for w in DBSession.query(WordyWord.word).filter(WordyWord.word.in_(words)).limit(len(words))]

def get_player_name(player_id):
    return DBSession.query(User.actual_name).filter(User.id == player_id).one()[0]

def update_game(the_game):
    pass
    # SQLAlchemy does this automatically for me but it's
    # here to make a hook easier for anything else

line_points = re.compile(r"(.+): [a-zA-Z ]+ for ([0-9]+) points")
def tally_scores(the_game):
    results = defaultdict(int)
    
    # Add it up from the turn log
    for l in the_game.turn_log.split("\n"):
        r = line_points.search(l.strip())
       
        if r != None:
            name, points = r.groups()
            results[name] += int(points)
    
    # Add in remaining tiles
    results[1] = sum([letter_values[l] for l in the_game.player1_tiles])
    results[2] = sum([letter_values[l] for l in the_game.player2_tiles])
    results[3] = sum([letter_values[l] for l in the_game.player2_tiles])
    results[4] = sum([letter_values[l] for l in the_game.player2_tiles])
    
    return results
