# engine/gamestate.py

from dataclasses import dataclass
from engine.card import Card


@dataclass(frozen=True)
class PlayerInfo:
    player_id: str
    name: str
    stack: int
    current_bet: int    # amount bet this street
    is_active: bool     # False once folded
    is_all_in: bool
    position: int       # seat index


@dataclass(frozen=True)
class Action:
    player_id: str
    player_name: str
    action_type: str    # "fold", "check", "call", "raise", "blind", "deal"
    amount: int
    pot_after: int
    street: str         # "preflop", "flop", "turn", "river"


@dataclass(frozen=True)
class GameState:
    # bot private info
    id: str
    hole_cards: tuple[Card, ...]

    # table
    community_cards: tuple[Card, ...]
    pot: int
    street: str

    # betting
    current_bet: int
    min_raise: int
    last_raiser_id: str | None

    # all players
    players: tuple[PlayerInfo, ...]

    # tracking
    hand_number: int
    action_history: tuple[Action, ...]

    @property
    def info(self) -> PlayerInfo:
        return next(p for p in self.players if p.player_id == self.id)

    @property
    def stack(self) -> int:
        return self.info.stack

    @property
    def active_players(self) -> tuple[PlayerInfo, ...]:
        return tuple(p for p in self.players if p.is_active)

    @property
    def amount_to_call(self) -> int:
        return max(0, self.current_bet - self.info.current_bet)

    @property
    def pot_odds(self) -> float | None:
        if self.amount_to_call == 0:
            return None
        return self.amount_to_call / (self.pot + self.amount_to_call)