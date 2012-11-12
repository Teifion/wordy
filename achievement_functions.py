from ...models import (
    DBSession,
)

from .achievement_models import AchievementType
import transaction

def register(achievement_list):
    """Takes a list of achievement type (or dict) and ensures they exist
    within the database. Any type not in the database is added."""
    
    # If it's a dictionary convert it into an AchievementType
    achievement_list = [AchievementType(*a) if type(a) == tuple else a for a in achievement_list]
    
    return
    
    # Who are we missing?
    names = [a.name for a in achievement_list]
    found = []
    for n in DBSession.query(AchievementType.name).filter(AchievementType.name.in_(names)):
        found.append(n[0])
    
    with transaction.manager:
        for a in achievement_list:
            if a.name not in found:
                DBSession.add(a)
