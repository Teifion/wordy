from sqlalchemy import (
    Column,
    Integer,
    Text,
    String,
    ForeignKey,
)

# You will need to point this to wherever your declarative base is
from ...models import Base

class WordyGame(Base):
    __tablename__ = 'wordy_games'
    id          = Column(Integer, primary_key=True)
    turn        = Column(Integer, nullable=False, default=0)
    turn_log    = Column(Text, nullable=False, default='')
    
    # We're storing the board as a string because we shouldn't be asking for specific
    # parts of the board in database queries and we know the exact size and layout
    # of the board so we can easily pull pieces from it as if it were an array
    # while at the same time we're storing character data in it
    # It defaults to a blank board
    board       = Column(String, nullable=False, default=' '*255)
    
    # We're assuming a table called users with a property of "id"
    # I would normally have used PostgreSQL arrays but wanted to keep
    # it database agnostic
    player1     = Column(Integer, ForeignKey("users.id"))
    player2     = Column(Integer, ForeignKey("users.id"))
    player3     = Column(Integer, ForeignKey("users.id"), nullable=True)
    player4     = Column(Integer, ForeignKey("users.id"), nullable=True)

class WordyWord(Base):
    __tablename__ = 'wordy_words'
    id   = Column(Integer, primary_key=True)
    word = Column(String, nullable=False)
