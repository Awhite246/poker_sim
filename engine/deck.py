# engine/deck.py

from engine.card import Card, Rank, Suit
import random

class Deck:
    def __init__(self):
        self.cards: list[Card] = [
            Card(rank, suit)
            for rank in Rank
            for suit in Suit
        ]
        
    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self, num_cards: int) -> list[Card]:
        if num_cards < 1:
            raise ValueError(f"num_cards must be at least 1, got {num_cards}")
        if num_cards > len(self.cards):
            raise ValueError(f"Not enough cards left — requested {num_cards}, only {len(self.cards)} remaining")
        
        dealt = [self.cards.pop() for _ in range(num_cards)]
        return dealt
    
    def reset(self) -> None:
        """Rebuild and reshuffle — call between hands"""
        self.__init__()

    def __len__(self) -> int:
        return len(self.cards)

    def __repr__(self) -> str:
        return f"Deck({len(self.cards)} cards remaining)"