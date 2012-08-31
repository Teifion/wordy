

def string_to_board(board_string):
    the_board = []
    
    for r in range(15):
        a = r * 15
        b = r * 15 + 15
        the_board.append(board_string[a:b])
    
    return the_board


