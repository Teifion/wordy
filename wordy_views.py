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
@view_config(route_name='games/wordy/init', renderer='templates/wordy_blank.pt', permission='view')
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

@view_config(route_name='games/wordy', renderer='templates/wordy_menu.pt', permission='view')
def wordy_menu(request):
    # I've got my userid tied into the request object via the authentication system
    user_id = request.user.id
    
    game_list = DBSession.query(WordyGame).filter(or_(
        WordyGame.player1 == user_id,
        WordyGame.player2 == user_id,
        WordyGame.player3 == user_id,
        WordyGame.player4 == user_id,
    ))
    
    user_ids = []
    for g in game_list:
        user_ids.append(g.player1)
        user_ids.append(g.player2)
        
        # These could be null
        if g.player3: user_ids.append(g.player3)
        if g.player4: user_ids.append(g.player4)
    
    user_ids = set(user_ids)
    usernames = {}
    for uid, uname in DBSession.query(User.id, User.name).filter(User.id.in_(user_ids)).limit(len(user_ids)):
        usernames[uid] = uname
    
    layout = get_renderer('../../templates/layouts/empty.pt').implementation()
    
    return dict(
        title         = "Wordy",
        game_list     = game_list,
        usernames     = usernames,
        layout        = layout,
    )

@view_config(route_name='games/wordy/new_game', renderer='templates/new_game.pt', permission='view')
def new_game(request):
    layout = get_renderer('../../templates/layouts/empty.pt').implementation()
    
    if "form.submitted" in request.params:
        opponent_name = request.params['opponent_name'].strip().upper()
        
        opponent_id = DBSession.query(User.id).filter(User.name == opponent_name).one()[0]
        
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
        title        = "Wordy - New game",
        layout       = layout,
    )

@view_config(route_name='games/wordy/game', renderer='templates/wordy_game.pt', permission='view')
def view_game(request):
    layout = get_renderer('../../templates/layouts/empty.pt').implementation()
    
    game_id = int(request.matchdict['game_id'])
    the_game = DBSession.query(WordyGame).filter(WordyGame.id == game_id).first()
    
    if the_game.player1 == request.user.id:
        letters = the_game.player1_tiles
        other_player = DBSession.query(User).filter(User.id == the_game.player2).one()
    elif the_game.player2 == request.user.id:
        letters = the_game.player2_tiles
        other_player = DBSession.query(User).filter(User.id == the_game.player1).one()
    elif the_game.player3 == request.user.id: letters = the_game.player3_tiles
    elif the_game.player4 == request.user.id: letters = the_game.player4_tiles
    else:
        raise Exception("You are not a player")
    
    the_board = wordy_functions.string_to_board(the_game.board.lower())
    
    return dict(
        title        = "Wordy - Playing {}".format(other_player.actual_name),
        layout       = layout,
        the_board    = the_board,
        player_letters = list(letters.lower()),
        the_game = the_game,
    )

@view_config(route_name='games/wordy/make_move', renderer='string', permission='view')
def make_move(request):
    game_id = int(request.matchdict['game_id'])
    the_game = DBSession.query(WordyGame).filter(WordyGame.id == game_id).first()
    
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
        result = wordy_functions.attempt_move(the_game, new_letters)
    except Exception as e:
        result = e.args[0]
    
    if result == "success":
        return "failure:Success"
    
    else:
        return "failure:%s" % result
    

@view_config(route_name='games/wordy/check_status', renderer='templates/wordy_game.pt', permission='view')
def check_status(request):
    layout = get_renderer('../../templates/layouts/empty.pt').implementation()
    
    return dict(
        title         = "wordy",
        layout        = layout,
    )

@view_config(route_name='games/wordy/get_updated_board', renderer='templates/wordy_game.pt', permission='view')
def get_updated_board(request):
    layout = get_renderer('../../templates/layouts/empty.pt').implementation()
    
    return dict(
        title         = "wordy",
        layout        = layout,
    )
