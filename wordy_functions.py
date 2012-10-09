import random

default_bag = "EEEEEEEEEEEEAAAAAAAAAIIIIIIIIIOOOOOOOONNNNNNRRRRRRTTTTTTLLLLSSSSUUUUDDDDGGGBBCCMMPPFFHHVVWWYYKJXQZ****"

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

def attempt_move(the_game, new_letters):
    b = string_to_board(the_game.board)
    
    # First we want to make sure all the letters can be placed in these locations
    xs, ys = set(), set()
    for l, x, y in new_letters:
        if x < 0 or x > 14 or y < 0 or y > 14:
            raise KeyError("{},{} is not a valid tile (15x15 board size)".format(x, y))
        
        if b[y][x] != " ":
            raise KeyError("{},{} is already occupied by a letter".format(x, y))
        
        b[y][x] = l
        
        xs.add(x)
        ys.add(y)
    
    if len(xs) > 1 and len(ys) > 1:
        raise KeyError("You must place all your tiles in one row or one column")
    
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
    words = []
    
    # start with cross scans, we can scan all words on the board but if we limit searches
    # it reduces complexity of database queries
    for x in xs:
        current_word = []
        
        for y in range(0,15):
            l = b[y][x]
            if l == " ":
                if current_word != []:
                    if len(current_word) > 1:
                        words.append("".join(current_word))
                    current_word = []
            else:
                current_word.append(l)
            
        if len(current_word) > 1:
            words.append("".join(current_word))
                
    # Now vertical scans
    for y in ys:
        current_word = []
        
        for x in range(0,15):
            l = b[y][x]
            if l == " ":
                if current_word != []:
                    if len(current_word) > 1:
                        words.append("".join(current_word))
                    current_word = []
            else:
                current_word.append(l)
        
        if len(current_word) > 1:
            words.append("".join(current_word))
    
    print("\n\n")
    print(xs)
    print(ys)
    print(words)
    
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
    
    # _pp_board(b)
    
    return "Success"


# This is a function you might need to alter to get at the words from the database
from ...models import (
    DBSession,
    WordyWord,
)

def get_words_from_db(words):
    return [w[0] for w in DBSession.query(WordyWord.word).filter(WordyWord.word.in_(words)).limit(len(words))]
