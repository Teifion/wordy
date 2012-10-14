Wordy is based on Scrabble (as it's a trademark I was advised to pick a different name).

This game was designed to be used primarily as part of a Pyramid application (using SQLAlchemy) but at the same time to be as pluggable as possible. All the Pyramid related code is thus in the scrabble_views and scrabble_models while the game code is as separate from the framework as possible.

I made this project to add to a program at work. This software is relased under a BSD license (do what you want with it but I'm not to blame for anything that happens as a result).

I got the wordlist from http://www.becomeawordgameexpert.com/wordlists.htm, there are loads of other very cool word lists on that page, well worth a look at too.



You'll want to add the following paths for a Pyramid application:

    config.add_route('games/wordy', '/games/wordy')
    config.add_route('games/wordy/init', '/games/wordy/init')
    config.add_route('games/wordy/game', '/games/wordy/game/{game_id}')
    config.add_route('games/wordy/new_game', '/games/wordy/new_game')
    config.add_route('games/wordy/test_move', '/games/wordy/test_move/{game_id}')
    config.add_route('games/wordy/make_move', '/games/wordy/make_move/{game_id}')
    config.add_route('games/wordy/check_status', '/games/wordy/check_status/{game_id}')
    config.add_route('games/wordy/get_updated_board', '/games/wordy/get_updated_board/{game_id}')
