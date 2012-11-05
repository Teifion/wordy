import transaction

from pyramid.view import (
    view_config,
)

from pyramid.httpexceptions import (
    HTTPFound,
)

from pyramid.renderers import get_renderer
from sqlalchemy import or_

from ...models import (
    DBSession,
    User,
    WordyGame,
)

from . import wordy_functions
# After installation you should remove this view or block it off in some way
@view_config(route_name='games/wordy/init', renderer='templates/wordy_blank.pt', permission='code')
def wordy_init(request):
    layout = get_renderer('../../templates/layouts/empty.pt').implementation()
    
    if "form.submitted" in request.params:
        f = request.params['wordlist'].file
        
        try:
            words = f.read().decode('latin-1')
        except Exception:
            words = f.read().decode('utf-8')
        
        # We're splitting by space but it might be we should watch for
        # line returns and commas too
        words = words.replace("\n", " ").replace(",", " ")
        
        # Filter out empty words (just incase)
        word_list = filter(
            lambda x: x != "",
            [s.strip() for s in words.split(" ")]
        )
        
        # Build query
        query = "INSERT INTO wordy_words (word) VALUES {}".format(
            ",".join(["('%s')" % w.replace("'", "''") for w in word_list])
        )
        
        with transaction.manager:
            DBSession.execute("DELETE FROM wordy_words")
            DBSession.execute(query)
            DBSession.execute("COMMIT")
        
        content = "Wordlist inserted correctly"
    else:
        content = """
        <form tal:condition="the_doc != None" action="{route}" method="post" accept-charset="utf-8" style="padding:10px;" enctype="multipart/form-data">
            
            <label for="wordlist">Wordlist file:</label>
            <input type="file" name="wordlist" size="40">
            <br />
            
            <input type="submit" name="form.submitted" />
        </form>
        """.format(
            route = request.route_url('games/wordy/init')
        )
    
    return dict(
        title   = "Wordy installation",
        layout  = layout,
        content = content,
    )

@view_config(route_name='games/wordy', renderer='templates/wordy_menu.pt', permission='loggedin')
def wordy_menu(request):
    # I've got my userid tied into the request object via the authentication system
    user_id = request.user.id
    
    game_list = list(DBSession.query(WordyGame).filter(or_(
        WordyGame.player1 == user_id,
        WordyGame.player2 == user_id,
        WordyGame.player3 == user_id,
        WordyGame.player4 == user_id,
    )))
    
    user_ids = []
    your_turn = []
    their_turn = []
    ended_games = []
    for g in game_list:
        cturn = wordy_functions.player_turn(g.turn)
        
        user_ids.append(g.player1)
        user_ids.append(g.player2)
        
        if g.winner != None:
            if g.player1 == user_id:
                g.opponent = g.player2
            else:
                g.opponent = g.player1
            
            ended_games.append(g)
            continue
        
        if cturn == 1:
            if g.player1 == user_id:
                your_turn.append(g)
                g.opponent = g.player2
            else:
                their_turn.append(g)
                g.opponent = g.player1
        elif cturn == 2:
            if g.player2 == user_id:
                your_turn.append(g)
                g.opponent = g.player1
            else:
                their_turn.append(g)
                g.opponent = g.player2
        
        # These could be null
        if g.player3: user_ids.append(g.player3)
        if g.player4: user_ids.append(g.player4)
    
    user_ids = set(user_ids)
    usernames = {}
    for uid, uname in DBSession.query(User.id, User.name).filter(User.id.in_(user_ids)).limit(len(user_ids)):
        usernames[uid] = uname
    usernames[-1] = "Draw"
    
    layout = get_renderer('../../templates/layouts/empty.pt').implementation()
    
    return dict(
        title      = "Wordy",
        game_list  = game_list,
        usernames  = usernames,
        layout     = layout,
        your_turn  = your_turn,
        their_turn = their_turn,
        ended_games = ended_games,
    )

@view_config(route_name='games/wordy/new_game', renderer='templates/new_game.pt', permission='loggedin')
def new_game(request):
    message = ""
    flash_colour = "A00"
    layout  = get_renderer('../../templates/layouts/empty.pt').implementation()
    opponent_name = request.params.get('opponent_name', '').strip().upper()
    
    if "form.submitted" in request.params and opponent_name != "":
        opponent_id = DBSession.query(User.id).filter(User.name == opponent_name).first()
        
        if opponent_id == None:
            message = """I'm sorry, we can't find anbody by the name of "{}" """.format(request.params['opponent_name'].strip())
            return dict(
                title        = "Wordy - New game",
                layout       = layout,
                message      = message,
                flash_colour = flash_colour,
                opponent_name = request.params['opponent_name'].strip(),
            )
        
        opponent_id = opponent_id[0]
        new_game = WordyGame()
        new_game.player1 = request.user.id
        new_game.player2 = opponent_id
        
        # Setup the initial tiles
        the_bag = wordy_functions.default_bag
        
        new_game.player1_tiles, the_bag = wordy_functions.pick_from_bag(the_bag, tiles=7)
        new_game.player2_tiles, the_bag = wordy_functions.pick_from_bag(the_bag, tiles=7)
        new_game.game_bag = str(the_bag)
        
        DBSession.add(new_game)
        DBSession.flush()
        
        return HTTPFound(location = request.route_url('games/wordy/game', game_id=new_game.id))
    
    return dict(
        title         = "Wordy - New game",
        layout        = layout,
        message       = message,
        flash_colour  = flash_colour,
        opponent_name = "",
    )

@view_config(route_name='games/wordy/game', renderer='templates/wordy_game.pt', permission='loggedin')
def view_game(request):
    layout = get_renderer('../../templates/layouts/empty.pt').implementation()
    
    game_id = int(request.matchdict['game_id'])
    the_game = DBSession.query(WordyGame).filter(WordyGame.id == game_id).first()
    
    your_turn = False
    if the_game.player1 == request.user.id:
        letters = the_game.player1_tiles
        other_player = DBSession.query(User).filter(User.id == the_game.player2).one()
        if wordy_functions.player_turn(the_game.turn) == 1: your_turn = True
    elif the_game.player2 == request.user.id:
        letters = the_game.player2_tiles
        other_player = DBSession.query(User).filter(User.id == the_game.player1).one()
        if wordy_functions.player_turn(the_game.turn) == 2: your_turn = True
    elif the_game.player3 == request.user.id: letters = the_game.player3_tiles
    elif the_game.player4 == request.user.id: letters = the_game.player4_tiles
    else:
        raise Exception("You are not a player")
    
    the_board = wordy_functions.string_to_board(the_game.board.lower())
    scores = wordy_functions.tally_scores(the_game.turn_log)
    
    turn_log = []
    for l in the_game.turn_log.split("\n"):
        turn_log.append(l)
    
    return dict(
        title        = "Wordy - Playing {}".format(other_player.actual_name),
        layout       = layout,
        the_board    = the_board,
        player_letters = list(letters.lower()),
        turn_log = "<br />".join(turn_log),
        the_game = the_game,
        your_turn = your_turn,
        scores = scores,
    )

@view_config(route_name='games/wordy/make_move', renderer='string', permission='loggedin')
def make_move(request):
    game_id = int(request.matchdict['game_id'])
    the_game = DBSession.query(WordyGame).filter(WordyGame.id == game_id).first()
    
    # Special "moves"
    if "forfeit" in request.params:
        wordy_functions.forfeit_game(the_game, request.user.id)
        return HTTPFound(location = request.route_url('games/wordy/game', game_id=the_game.id))
    
    if "swap" in request.params:
        wordy_functions.swap_letters(the_game, request.user.id)
        return HTTPFound(location = request.route_url('games/wordy/game', game_id=the_game.id))
    
    if the_game.player1 == request.user.id:
        player_letters = the_game.player1_tiles
    elif the_game.player2 == request.user.id:
        player_letters = the_game.player2_tiles
    elif the_game.player3 == request.user.id:
        player_letters = the_game.player3_tiles
    elif the_game.player4 == request.user.id:
        player_letters = the_game.player4_tiles
    
    new_letters = []
    
    result = []
    for k, tile_info in request.params.items():
        if tile_info != "":
            l, x, y = tile_info.split("_")
            new_letters.append((player_letters[int(l)], int(x), int(y)))
    
    if new_letters == []:
        return "failure:You didn't make a move"
    
    try:
        result = "success:%s" % wordy_functions.perform_move(the_game, request.user.id, new_letters)
    except Exception as e:
        result = "failure:%s" % e.args[0]
    
    return result

@view_config(route_name='games/wordy/test_move', renderer='string', permission='view')
def test_move(request):
    game_id = int(request.matchdict['game_id'])
    the_game = DBSession.query(WordyGame).filter(WordyGame.id == game_id).one()
    
    if the_game.player1 == request.user.id:
        player_letters = the_game.player1_tiles
    elif the_game.player2 == request.user.id:
        player_letters = the_game.player2_tiles
    elif the_game.player3 == request.user.id:
        player_letters = the_game.player3_tiles
    elif the_game.player4 == request.user.id:
        player_letters = the_game.player4_tiles
    
    new_letters = []
    
    result = []
    for k, tile_info in request.params.items():
        if tile_info != "":
            l, x, y = tile_info.split("_")
            new_letters.append((player_letters[int(l)], int(x), int(y)))
    
    if new_letters == []:
        return "failure:You didn't make a move"
    
    try:
        result = wordy_functions.attempt_move(the_game, request.user.id, new_letters)
    except Exception:
        result = 0
    
    return result

# Is it my turn yet?
@view_config(route_name='games/wordy/check_status', renderer='string', permission='loggedin')
def check_status(request):
    game_id = int(request.matchdict['game_id'])
    t, p1, p2 = DBSession.query(WordyGame.turn, WordyGame.player1, WordyGame.player2).filter(WordyGame.id == game_id).one()
    
    your_turn = False
    
    player_turn = wordy_functions.player_turn(t)
    if player_turn == 1 and request.user.id == p1: your_turn = True
    if player_turn == 2 and request.user.id == p2: your_turn = True
    
    return str(your_turn)

@view_config(route_name='games/wordy/get_updated_board', renderer='templates/wordy_game.pt', permission='loggedin')
def get_updated_board(request):
    layout = get_renderer('../../templates/layouts/empty.pt').implementation()
    
    return dict(
        title         = "wordy",
        layout        = layout,
    )
