# engine/hand_eval.py

from treys import Evaluator, Card as TreysCard
from engine.card import Card

_evaluator = Evaluator()

def _to_treys(card: Card) -> int:
    rank_map = {
        2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7",
        8: "8", 9: "9", 10: "T", 11: "J", 12: "Q", 13: "K", 14: "A"
    }
    rank = rank_map[card.rank.value]
    suit = card.suit.value  # "c", "d", "h", "s" — matches treys format
    return TreysCard.new(rank + suit)


def evaluate(hole_cards: tuple[Card, ...], community_cards: tuple[Card, ...]) -> int:
    """Lower score = better hand. 1 is a royal flush, 7462 is the worst hand."""
    treys_hole      = [_to_treys(c) for c in hole_cards]
    treys_community = [_to_treys(c) for c in community_cards]
    return _evaluator.evaluate(treys_community, treys_hole)


def rank_players(hands: dict[str, int]) -> list[list[str]]:
    """
    Same interface as before — returns players grouped by rank, best first.
    Treys scores are inverted (lower = better) so we sort ascending.
    """
    grouped: dict[int, list[str]] = {}
    for player_id, score in hands.items():
        grouped.setdefault(score, []).append(player_id)
    return [group for _, group in sorted(grouped.items())]


def describe(hole_cards: tuple[Card, ...], community_cards: tuple[Card, ...]) -> str:
    score = evaluate(hole_cards, community_cards)
    rank  = _evaluator.get_rank_class(score)
    return _evaluator.class_to_string(rank)