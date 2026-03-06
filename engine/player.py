# engine/player.py

from abc import ABC, abstractmethod
from engine.gamestate import GameState, Action


class Player(ABC):

    def __init__(self, name: str):
        self.name = name
        self.__player_id = None  # set by the engine on registration, never touch this

    @property
    def player_id(self) -> str:
        return self.__player_id

    def update_state(self, action: Action, state: GameState) -> None:
        # called after every action by any player — override to track opponents
        pass

    @abstractmethod
    def decide_action(self, state: GameState) -> tuple[str, int]:
        # called when it's your turn — must return ("fold"|"check"|"call"|"raise", amount)
        ...