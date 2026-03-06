# engine/player_record.py

from dataclasses import dataclass, field
from engine.card import Card
from engine.player import Player


@dataclass
class PlayerRecord:
    player_id: str
    bot: Player
    stack: int
    hole_cards: list[Card] = field(default_factory=list)
    current_bet: int = 0
    is_active: bool = True
    is_all_in: bool = False
    position: int = 0

    def reset_for_new_hand(self) -> None:
        self.hole_cards = []
        self.current_bet = 0
        self.is_active = True
        self.is_all_in = False

    def reset_for_new_street(self) -> None:
        self.current_bet = 0

    def post_blind(self, amount: int) -> int:
        # returns the actual amount posted in case they can't cover it
        actual = min(amount, self.stack)
        self.stack -= actual
        self.current_bet = actual
        if self.stack == 0:
            self.is_all_in = True
        return actual

    def place_bet(self, amount: int) -> int:
        # amount is the total bet, not the raise on top
        additional = amount - self.current_bet
        actual = min(additional, self.stack)
        self.stack -= actual
        self.current_bet += actual
        if self.stack == 0:
            self.is_all_in = True
        return self.current_bet

    def fold(self) -> None:
        self.is_active = False
        self.hole_cards = []