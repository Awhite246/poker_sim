# engine/logger.py

import logging
from engine.gamestate import Action
from engine.player_record import PlayerRecord


def setup_logger(level: int = logging.DEBUG, log_file: str | None = None) -> logging.Logger:
    logger = logging.getLogger("poker_engine")
    logger.setLevel(level)

    formatter = logging.Formatter("[%(asctime)s] %(message)s", datefmt="%H:%M:%S")

    # always log to console
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)

    # optionally also write to a file
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


_logger = setup_logger(level=logging.INFO, log_file="tournament.log")


def log_new_hand(hand_number: int, records: dict) -> None:
    _logger.info(f"--- Hand #{hand_number} ---")
    for r in records.values():
        _logger.debug(f"  {r.bot.name}: ${r.stack}")


def log_hole_cards(records: dict) -> None:
    for r in records.values():
        cards = " ".join(str(c) for c in r.hole_cards)
        _logger.debug(f"  {r.bot.name} dealt: {cards}")


def log_community_cards(street: str, community_cards: list) -> None:
    cards = " ".join(str(c) for c in community_cards)
    _logger.info(f"{street.capitalize()}: {cards}")


def log_action(action: Action) -> None:
    match action.action_type:
        case "fold":
            _logger.info(f"  {action.player_name} folds")
        case "check":
            _logger.info(f"  {action.player_name} checks")
        case "call":
            _logger.info(f"  {action.player_name} calls ${action.amount}")
        case "raise":
            _logger.info(f"  {action.player_name} raises to ${action.amount}")
        case "blind":
            _logger.info(f"  {action.player_name} posts blind ${action.amount}")
        case _:
            _logger.debug(f"  {action.player_name} {action.action_type} ${action.amount}")


def log_winner(winners: list[PlayerRecord], pot: int, hand_name: str | None = None) -> None:
    names = ", ".join(w.bot.name for w in winners)
    hand  = f" with {hand_name}" if hand_name else ""
    _logger.info(f"  {names} wins ${pot}{hand}")


def log_showdown(records: dict, descriptions: dict[str, str]) -> None:
    _logger.info("--- Showdown ---")
    for r in records.values():
        if r.is_active:
            cards     = " ".join(str(c) for c in r.hole_cards)
            hand_name = descriptions.get(r.player_id, "?")
            _logger.info(f"  {r.bot.name}: {cards} — {hand_name}")


def log_bust(name: str, hand_number: int) -> None:
    _logger.info(f"  {name} busted out on hand #{hand_number}")


def log_tournament_result(records: dict) -> None:
    _logger.info("--- Tournament Over ---")
    standings = sorted(records.values(), key=lambda r: r.stack, reverse=True)
    for i, r in enumerate(standings, 1):
        _logger.info(f"  {i}. {r.bot.name}: ${r.stack}")