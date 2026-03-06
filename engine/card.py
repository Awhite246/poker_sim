# engine/card.py

from enum import Enum
from dataclasses import dataclass
from functools import total_ordering

class Suit(Enum):
    CLUBS    = "c"
    DIAMONDS = "d"
    HEARTS   = "h"
    SPADES   = "s"

class Rank(Enum):
    TWO   = 2
    THREE = 3
    FOUR  = 4
    FIVE  = 5
    SIX   = 6
    SEVEN = 7
    EIGHT = 8
    NINE  = 9
    TEN   = 10
    JACK  = 11
    QUEEN = 12
    KING  = 13
    ACE   = 14  # High ace — handle low ace in hand evaluation

@total_ordering
@dataclass(frozen=True)
class Card:
    rank: Rank
    suit: Suit

    def __str__(self) -> str:
        rank_symbols = {
            Rank.TEN: "T", Rank.JACK: "J", Rank.QUEEN: "Q",
            Rank.KING: "K", Rank.ACE: "A"
        }
        rank_str = rank_symbols.get(self.rank, str(self.rank.value))
        return f"{rank_str}{self.suit.value}"  # e.g. "As", "Td", "7h"

    def __repr__(self) -> str:
        return f"Card({str(self)})"

    # Ordering is by rank only — suits are equal in standard poker
    def __lt__(self, other: "Card") -> bool:
        return self.rank.value < other.rank.value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Card):
            return NotImplemented
        return self.rank == other.rank and self.suit == other.suit

    def __hash__(self):
        return hash((self.rank, self.suit))

    @staticmethod
    def from_string(s: str) -> "Card":
        """Parse a card from shorthand notation, e.g. 'As', 'Td', '7h'"""
        rank_map = {
            "2": Rank.TWO,   "3": Rank.THREE, "4": Rank.FOUR,
            "5": Rank.FIVE,  "6": Rank.SIX,   "7": Rank.SEVEN,
            "8": Rank.EIGHT, "9": Rank.NINE,  "T": Rank.TEN,
            "J": Rank.JACK,  "Q": Rank.QUEEN, "K": Rank.KING,
            "A": Rank.ACE
        }
        suit_map = {"c": Suit.CLUBS, "d": Suit.DIAMONDS,
                    "h": Suit.HEARTS, "s": Suit.SPADES}

        s = s.strip()
        if len(s) != 2:
            raise ValueError(f"Invalid card string: '{s}'")
        rank_str, suit_str = s[0].upper(), s[1].lower()

        if rank_str not in rank_map:
            raise ValueError(f"Invalid rank: '{rank_str}'")
        if suit_str not in suit_map:
            raise ValueError(f"Invalid suit: '{suit_str}'")

        return Card(rank=rank_map[rank_str], suit=suit_map[suit_str])