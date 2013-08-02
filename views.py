import transaction
import datetime

from pyramid.view import (
    view_config,
)

from pyramid.httpexceptions import (
    HTTPFound,
)

from pyramid.renderers import get_renderer
from sqlalchemy import or_

from ...achievements import achievement_functions
from . import wordy_functions, wordy_achievements

from ...models import (
    DBSession,
    User,
    WordyGame,
)

# After installation you should remove this view or block it off in some way
def wordy_init(request):
    layout = get_renderer('../../templates/layouts/viewer.pt').implementation()
    
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
        
        # Register the achievements
        achievement_functions.register(wordy_achievements.achievements)
        
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

def wordy_menu(request):
    # I've got my userid tied into the request object via the authentication system
    user_id = request.user.id
    
    game_list = list(DBSession.query(WordyGame).filter("'{:d}' = ANY ({})".format(int(user_id), "wordy_games.players")))
    
    user_ids = []
    your_turn = []
    their_turn = []
    ended_games = []
    for g in game_list:
        cturn = wordy_functions.player_turn(g)
        user_ids.extend(g.players)
        
        # Get a list of all the players in the game who are not us
        g.opponents = list(filter(None, [None if p == user_id else p for p in g.players]))
        
        if g.winner != None:
            ended_games.append(g)
            continue
        
        current_player = g.players[cturn]
        if current_player == user_id:
            your_turn.append(g)
        else:
            their_turn.append(g)
    
    user_ids = set(user_ids)
    usernames = {}
    for uid, uname in DBSession.query(User.id, User.name).filter(User.id.in_(user_ids)).limit(len(user_ids)):
        usernames[uid] = uname
    usernames[-1] = "Draw"
    
    layout = get_renderer('../../templates/layouts/viewer.pt').implementation()
    
    return dict(
        title      = "Wordy",
        game_list  = game_list,
        usernames  = usernames,
        layout     = layout,
        your_turn  = your_turn,
        their_turn = their_turn,
        ended_games = ended_games,
        now = datetime.datetime.now(),
    )

def new_game(request):
    message = ""
    flash_colour = "A00"
    layout  = get_renderer('../../templates/layouts/viewer.pt').implementation()
    
    if "form.submitted" in request.params:
        opponents = list(filter(None, [
            request.params['opponent_name1'].strip().upper(),
            request.params['opponent_name2'].strip().upper(),
            request.params['opponent_name3'].strip().upper(),
        ]))
        
        found_opponents = []
        found_names = []
        for uid, uname in DBSession.query(User.id, User.name).filter(User.name.in_(opponents)).limit(len(opponents)):
            found_opponents.append(uid)
            found_names.append(uname)
        
        if len(found_opponents) != len(opponents):
            message = """I'm sorry, we can't find all your opponents"""
            return dict(
                title        = "Wordy - New game",
                layout       = layout,
                message      = message,
                flash_colour = flash_colour,
            )
        
        new_game = WordyGame()
        new_game.players = [request.user.id] + found_opponents
        new_game.last_move = datetime.datetime.now()
        
        # Setup the initial tiles
        the_bag = wordy_functions.default_bag
        new_game.tiles = []
        
        for p in new_game.players:
            new_tiles, the_bag = wordy_functions.pick_from_bag(the_bag, tiles=7)
            new_game.tiles.append(new_tiles)
        
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

def view_game(request):
    layout = get_renderer('../../templates/layouts/viewer.pt').implementation()
    
    game_id = int(request.matchdict['game_id'])
    the_game = DBSession.query(WordyGame).filter(WordyGame.id == game_id).first()
    
    # Get our player number
    player_number = wordy_functions.player_number(the_game, request.user.id)
    
    pturn = wordy_functions.player_turn(the_game)
    
    if player_number == None:
        letters = ""
        spectator = True
    else:
        letters = the_game.tiles[player_number]
        spectator = False
    
    the_board = wordy_functions.string_to_board(the_game.board.lower())
    scores = wordy_functions.tally_scores(the_game, count_tiles=False)
    
    turn_log = []
    for l in the_game.turn_log.split("\n"):
        turn_log.append(l)
    
    return dict(
        title        = "Wordy",
        layout       = layout,
        the_board    = the_board,
        player_letters = list(letters.lower()),
        turn_log = "<br />".join(turn_log),
        the_game = the_game,
        your_turn = (the_game.players[pturn] == request.user.id),
        whose_turn = wordy_functions.get_player_name(the_game.players[pturn]),
        scores = scores,
        now = datetime.datetime.now(),
        spectator = spectator,
    )

def make_move(request):
    game_id = int(request.matchdict['game_id'])
    the_game = DBSession.query(WordyGame).filter(WordyGame.id == game_id).first()
    
    # Get our player number
    player_number = wordy_functions.player_number(the_game, request.user.id)
    
    # Special "moves"
    if "forfeit" in request.params:
        wordy_functions.forfeit_game(the_game, request.user.id)
        return HTTPFound(location = request.route_url('games/wordy/game', game_id=the_game.id))
    
    if "end_game" in request.params:
        wordy_functions.premature_end_game(the_game, request.user.id)
        return HTTPFound(location = request.route_url('games/wordy/game', game_id=the_game.id))
    
    if "swap" in request.params:
        wordy_functions.swap_letters(the_game, request.user.id)
        return HTTPFound(location = request.route_url('games/wordy/game', game_id=the_game.id))
    
    if "pass" in request.params:
        wordy_functions.pass_turn(the_game, request.user.id)
        return HTTPFound(location = request.route_url('games/wordy/game', game_id=the_game.id))
    
    player_letters = the_game.tiles[player_number]
    new_letters = []
    
    result = []
    for k, tile_info in request.params.items():
        if tile_info != "":
            l, x, y = tile_info.split("_")
            
            try:
                new_letters.append((player_letters[int(l)], int(x), int(y)))
            except Exception as e:
                return "failure:List index exception. I can't work out why this is happening or if you even see anything. If you do see this, please let Teifion know."
    
    if new_letters == []:
        return "failure:You didn't make a move"
    
    try:
        result = "success:%s" % wordy_functions.perform_move(the_game, request.user.id, new_letters)
    except KeyError as e:
        result = "failure:%s" % e.args[0]
    
    request.do_not_log = True
    return result

def test_move(request):
    game_id = int(request.matchdict['game_id'])
    the_game = DBSession.query(WordyGame).filter(WordyGame.id == game_id).first()
    
    # Get our player number
    player_number = wordy_functions.player_number(the_game, request.user.id)
    
    player_letters = the_game.tiles[player_number]
    
    new_letters = []
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
    
    request.do_not_log = True
    return result

# Is it my turn yet?
def check_status(request):
    game_id = int(request.matchdict['game_id'])
    the_game = DBSession.query(WordyGame).filter(WordyGame.id == game_id).one()
    pturn = wordy_functions.player_turn(the_game)
    
    request.do_not_log = True
    return str((the_game.players[pturn] == request.user.id))

def get_updated_board(request):
    layout = get_renderer('../../templates/layouts/viewer.pt').implementation()
    
    request.do_not_log = True
    return dict(
        title         = "wordy",
        layout        = layout,
    )
