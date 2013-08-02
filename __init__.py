def includeme(config):
    from . import views
    
    """
    Pass this to your configurator object like so:
    
    from . import connect_four
    config.include(connect_four, route_prefix="games/connect4")
    """
    
    config.add_route('wordy.init', 'wordy/init')
    config.add_route('wordy.menu', 'wordy/menu')
    config.add_route('wordy.new_game', 'wordy/new_game')
    config.add_route('wordy.game', 'wordy/game')
    config.add_route('wordy.make_move', 'wordy/make_move')
    config.add_route('wordy.test_move', 'wordy/test_move')
    config.add_route('wordy.check_status', 'wordy/check_status')
    config.add_route('wordy.get_updated_board', 'wordy/get_updated_board')
    
    config.add_view(views.init, route_name='wordy.init', renderer='templates/blank.pt', permission='code')
    config.add_view(views.menu, route_name='wordy.menu', renderer='templates/menu.pt', permission='loggedin')
    config.add_view(views.new_game, route_name='wordy.new_game', renderer='templates/new_game.pt', permission='loggedin')
    config.add_view(views.game, route_name='wordy.game', renderer='templates/game.pt', permission='loggedin')
    config.add_view(views.get_updated_board, route_name='wordy.get_updated_board', renderer='templates/game.pt', permission='loggedin')
    
    config.add_view(views.check_status, route_name='wordy.check_status', renderer='string', permission='loggedin')
    config.add_view(views.make_move, route_name='wordy.make_move', renderer='string', permission='loggedin')
    config.add_view(views.test_move, route_name='wordy.test_move', renderer='string', permission='view')
    
    return config
