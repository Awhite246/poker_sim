# engine/engine.py

import uuid
from engine.card import Card
from engine.deck import Deck
from engine.gamestate import GameState, PlayerInfo, Action
from engine.player import Player
from engine.player_record import PlayerRecord
from engine.gamestate import GameState, PlayerInfo, Action
from engine import hand_evaluator
from engine import logger as log

class PokerEngine:

    def __init__(self, small_blind: int, big_blind: int):
        self.small_blind = small_blind
        self.big_blind = big_blind
        self._records: dict[str, PlayerRecord] = {}
        self._deck = Deck()
        self._community_cards: list[Card] = []
        self._pot = 0
        self._current_bet = 0
        self._min_raise = big_blind
        self._last_raiser_id: str | None = None
        self._hand_number = 0
        self._action_history: list[Action] = []
        self._dealer_index = 0  # rotates each hand


    # Registration
    def register_player(self, bot: Player, starting_stack: int) -> str:
        player_id = str(uuid.uuid4())
        bot._Player__player_id = player_id
        position = len(self._records)
        self._records[player_id] = PlayerRecord(
            player_id=player_id,
            bot=bot,
            stack=starting_stack,
            position=position,
        )
        return player_id


    # Running the game
    def run_tournament(self, num_hands: int) -> None:
        for _ in range(num_hands):
            active = [r for r in self._records.values() if r.stack > 0]
            if len(active) < 2:
                print("Not enough players left, ending tournament")
                break
            self.run_hand()
        log.log_tournament_result(self._records)

    def run_hand(self) -> None:
        self._hand_number += 1
        self._reset_for_new_hand()
        log.log_new_hand(self._hand_number, self._records)
        self._deal_hole_cards()
        log.log_hole_cards(self._records)
        self._post_blinds()
        

        for street in ["preflop", "flop", "turn", "river"]:
            if street == "flop":
                self._deal_community(3)
            elif street in ("turn", "river"):
                self._deal_community(1)

            self._run_betting_round(street)

            # if everyone but one player has folded, end the hand early
            if len(self._active_records()) == 1:
                self._award_pot(self._active_records())
                return

        self._showdown()


    # Betting
    def _run_betting_round(self, street: str) -> None:
        self._current_bet = 0 if street != "preflop" else self.big_blind
        self._min_raise = self.big_blind
        self._last_raiser_id = None

        if street != "preflop":
            for record in self._records.values():
                record.reset_for_new_street()

        order = self._betting_order(street)
        acted = set()

        while True:
            remaining = [
                r for r in order
                if r.is_active and not r.is_all_in
                and (r.player_id not in acted or r.current_bet < self._current_bet)
            ]
            if not remaining:
                break

            # once everyone has acted and no one raised, close the round
            if all(r.player_id in acted for r in remaining):
                if all(r.current_bet == self._current_bet for r in remaining):
                    break

            record = remaining[0]
            state = self._build_game_state(record.player_id, street)
            action_type, amount = record.bot.decide_action(state)
            action = self._apply_action(record, action_type, amount, street)
            acted.add(record.player_id)

            self._action_history.append(action)
            self._broadcast(action)
            log.log_action(action)

    def _apply_action(self, record: PlayerRecord, action_type: str, amount: int, street: str) -> Action:
        if action_type == "fold":
            record.fold()

        elif action_type == "check":
            if self._current_bet > record.current_bet:
                # invalid check — treat as fold
                record.fold()
                action_type = "fold"

        elif action_type == "call":
            record.place_bet(self._current_bet)
            self._pot += self._current_bet - record.current_bet

        elif action_type == "raise":
            if amount < self._current_bet + self._min_raise:
                # raise too small — treat as call
                action_type = "call"
                record.place_bet(self._current_bet)
            else:
                self._min_raise = amount - self._current_bet
                self._current_bet = amount
                self._last_raiser_id = record.player_id
                added = record.place_bet(amount)
                self._pot += added

        return Action(
            player_id=record.player_id,
            player_name=record.bot.name,
            action_type=action_type,
            amount=amount,
            pot_after=self._pot,
            street=street,
        )

    def _post_blinds(self) -> None:
        records = list(self._records.values())
        sb_record = records[(self._dealer_index + 1) % len(records)]
        bb_record = records[(self._dealer_index + 2) % len(records)]

        sb_actual = sb_record.post_blind(self.small_blind)
        self._pot += sb_actual
        sb_action = Action(sb_record.player_id, sb_record.bot.name, "blind", sb_actual, self._pot, "preflop")
        self._action_history.append(sb_action)
        self._broadcast(sb_action)

        bb_actual = bb_record.post_blind(self.big_blind)
        self._pot += bb_actual
        bb_action = Action(bb_record.player_id, bb_record.bot.name, "blind", bb_actual, self._pot, "preflop")
        self._action_history.append(bb_action)
        self._broadcast(bb_action)


    # Dealing
    def _deal_hole_cards(self) -> None:
        for record in self._records.values():
            record.hole_cards = self._deck.deal(2)

    def _deal_community(self, n: int) -> None:
        self._community_cards.extend(self._deck.deal(n))
        log.log_community_cards(self._street, self._community_cards)


    # Showdown
    def _showdown(self) -> None:
        contenders = self._active_records()

        scores = {
            r.player_id: hand_evaluator.evaluate(
                tuple(r.hole_cards),
                tuple(self._community_cards),
            )
            for r in contenders
        }
        
        descriptions = {
            r.player_id: hand_evaluator.describe(
                tuple(r.hole_cards), tuple(self._community_cards)
            )
            for r in contenders
        }

        log.log_showdown(self._records, descriptions)
        ranked = hand_evaluator.rank_players(scores)
        winners = [self._records[pid] for pid in ranked[0]]
        log.log_winner(winners, self._pot, descriptions[ranked[0][0]])
        
        self._award_pot(winners)

    def _award_pot(self, contenders: list[PlayerRecord]) -> None:
        # TODO: side pot logic goes here
        if not contenders:
            return
        split = self._pot // len(contenders)
        for record in contenders:
            record.stack += split
        self._pot = 0


    # Helpers
    def _reset_for_new_hand(self) -> None:
        self._community_cards = []
        self._pot = 0
        self._current_bet = 0
        self._min_raise = self.big_blind
        self._last_raiser_id = None
        self._action_history = []
        self._deck.reset()
        self._deck.shuffle()
        self._dealer_index = (self._dealer_index + 1) % len(self._records)
        for record in self._records.values():
            record.reset_for_new_hand()

    def _active_records(self) -> list[PlayerRecord]:
        return [r for r in self._records.values() if r.is_active]

    def _betting_order(self, street: str) -> list[PlayerRecord]:
        records = list(self._records.values())
        n = len(records)
        if street == "preflop":
            # UTG acts first preflop (3 seats after dealer)
            start = (self._dealer_index + 3) % n
        else:
            # first active player left of dealer acts first post-flop
            start = (self._dealer_index + 1) % n
        ordered = records[start:] + records[:start]
        return [r for r in ordered if r.is_active and not r.is_all_in]

    def _build_game_state(self, player_id: str, street: str) -> GameState:
        record = self._records[player_id]
        return GameState(
            your_id=player_id,
            your_hole_cards=tuple(record.hole_cards),
            community_cards=tuple(self._community_cards),
            pot=self._pot,
            street=street,
            current_bet=self._current_bet,
            min_raise=self._min_raise,
            last_raiser_id=self._last_raiser_id,
            players=tuple(
                PlayerInfo(
                    player_id=r.player_id,
                    name=r.bot.name,
                    stack=r.stack,
                    current_bet=r.current_bet,
                    is_active=r.is_active,
                    is_all_in=r.is_all_in,
                    position=r.position,
                )
                for r in self._records.values()
            ),
            hand_number=self._hand_number,
            action_history=tuple(self._action_history),
        )

    def _broadcast(self, action: Action) -> None:
        for record in self._records.values():
            state = self._build_game_state(record.player_id, action.street)
            record.bot.update_state(action, state)