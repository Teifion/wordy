import transaction

from pyramid.view import (
    view_config,
)

from pyramid.renderers import get_renderer

from ...models import (
    DBSession,
)

from . import scrabble_functions
import sys

@view_config(route_name='games/scrabble/init', renderer='templates/scrabble_blank.pt', permission='view')
def scrabble_init(request):
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
        query = "INSERT INTO scrabble_words (word) VALUES {}".format(
            ",".join(["('%s')" % w.replace("'", "''") for w in word_list])
        )
        
        with transaction.manager:
            DBSession.execute("DELETE FROM scrabble_words")
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
            route = request.route_url('games/scrabble/init')
        )
    
    
    return dict(
        title   = "Scrabble",
        layout  = layout,
        content = content,
    )

@view_config(route_name='games/scrabble', renderer='scrabble_game.pt', permission='view')
def scrabble_menu(request):
    layout = get_renderer('../../templates/layouts/empty.pt').implementation()
    
    return dict(
        title         = "Scrabble",
        layout        = layout,
    )

@view_config(route_name='games/scrabble/game', renderer='scrabble_game.pt', permission='view')
def view_game(request):
    layout = get_renderer('../../templates/layouts/empty.pt').implementation()
    
    board_string = 'abcdefghijklmnopqrstuvwxyz' + ' '*229
    the_board = scrabble_functions.string_to_board(board_string)
    
    return dict(
        title         = "Scrabble",
        the_board     = the_board,
        layout        = layout,
    )

@view_config(route_name='games/scrabble/make_move', renderer='scrabble_game.pt', permission='view')
def make_move(request):
    layout = get_renderer('../../templates/layouts/empty.pt').implementation()
    
    return dict(
        title         = "Scrabble",
        layout        = layout,
    )

@view_config(route_name='games/scrabble/check_status', renderer='scrabble_game.pt', permission='view')
def check_status(request):
    layout = get_renderer('../../templates/layouts/empty.pt').implementation()
    
    return dict(
        title         = "Scrabble",
        layout        = layout,
    )

@view_config(route_name='games/scrabble/get_updated_board', renderer='scrabble_game.pt', permission='view')
def get_updated_board(request):
    layout = get_renderer('../../templates/layouts/empty.pt').implementation()
    
    return dict(
        title         = "Scrabble",
        layout        = layout,
    )