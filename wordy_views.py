import transaction

from pyramid.view import (
    view_config,
)

from pyramid.renderers import get_renderer
from sqlalchemy import or_

from ...models import (
    DBSession,
    User,
    WordyGame,
)

from . import wordy_functions

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

@view_config(route_name='games/wordy/game', renderer='templates/wordy_game.pt', permission='view')
def view_game(request):
    layout = get_renderer('../../templates/layouts/empty.pt').implementation()
    
    board_string = 'abcdefghijklmnopqrstuvwxyz' + ' '*229
    the_board = wordy_functions.string_to_board(board_string)
    
    return dict(
        title         = "wordy",
        the_board     = the_board,
        layout        = layout,
    )

@view_config(route_name='games/wordy/make_move', renderer='templates/wordy_game.pt', permission='view')
def make_move(request):
    layout = get_renderer('../../templates/layouts/empty.pt').implementation()
    
    return dict(
        title         = "wordy",
        layout        = layout,
    )

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
