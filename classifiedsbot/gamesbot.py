from dataclasses import dataclass
import random
from typing import List, Dict, Tuple
from games.card import Card
from forest.core import Bot, Message, run_bot
# from forest.pdictng import aPersistDict



@dataclass
class State:
    deck: List[Card]
    dealer_hand: List[Card]
    player_hand: List[Card]
    player_score: int
    dealer_score: int
    discard: List[Card]
    reset: bool




class BlackjackBot(Bot):
    def __init__(self) -> None:
        self.inst: Dict = {}
        # self.state: State = State(deck=[], player_hand=[], dealer_hand=[]) # , player_bet=0)
        super().__init__()

    # async def handle_message(self, message: Message) -> Response:
    #     if cmd := self.match_command(message):
    #         # invoke the function and return the response
    #         return await getattr(self, "do_" + cmd)(message)
    #     if len(message.full_text): # full_text can be empty during receipts and typing indicators
    #         if message.source.startswith('+'):
    #             source = message.source[1:]
    #         else:
    #             source = message.source

    def calc_hand(self, hand: List[List[Card]]) -> int:

        """Calculates the sum of the card values and accounts for aces"""
        non_aces = [c for c in hand if c.symbol != 'A']
        aces = [c for c in hand if c.symbol == 'A']
        cards_sum = 0
        for card in non_aces:
            if not card.down:
                if card.symbol in 'JQK': cards_sum += 10
                else: cards_sum += card.value
        for card in aces:
            if not card.down:
                if cards_sum <= 10: cards_sum += 11
                else: cards_sum += 1
        return cards_sum

    def make_deck(self) -> List[Card]:
        deck = [Card(suit, num) for num in range(2,15) for suit in Card.suits]
        random.shuffle(deck)
        return deck

    def visible(self, cards: list) -> list:
        out = []
        for card in cards:
            if card.down:
                out.append("X")
            else:
                out.append(card)
        return out


    async def do_db(self, message: Message) -> Tuple[str, Dict]:
        if message.source.startswith('+'):
            source = message.source[1:]
        else:
            source = message.source
        return self.inst[source]

    async def do_b(self, message: Message) -> str:
        return await self.blackjack_handler(message, flag = "init")
    async def do_blackjack(self, message: Message) -> str:
        return await self.blackjack_handler(message, flag = "init")
    async def do_hit(self, message: Message) -> str:
        return await self.blackjack_handler(message, flag = "hit")
    async def do_h(self, message: Message) -> str:
        return await self.blackjack_handler(message, flag = "hit")
    async def do_stand(self, message: Message) -> str:
        return await self.blackjack_handler(message=message, flag = "stand")
    async def do_s(self, message: Message) -> str:
        return await self.blackjack_handler(message=message, flag = "stand")

    def calc_score(self, source: str) -> tuple:
        
        if self.inst[source].player_score == 21 and self.inst[source].dealer_score == 21:
            result = ("Both blackjack.", 'tie')
        elif self.inst[source].player_score == 21:
            result = ("Player blackjack.", 'win')
        elif self.inst[source].dealer_score == 21:
            result = ("Dealer blackjack.", 'lose')
        elif self.inst[source].player_score > 21 and self.inst[source].dealer_score <= 21:
            result = ("You busted.", 'lose')
        elif self.inst[source].dealer_score > 21 and self.inst[source].player_score <= 21:
            result = ("Dealer busted.", 'win')
        elif self.inst[source].dealer_score > 21 and self.inst[source].player_score > 21:
            result = ("Both busted.", 'tie')
        else:
            result = ("Game continues.", 'continue')

        if result[1] == 'continue':
            dealer_hand = self.visible(self.inst[source].dealer_hand)
        else:
            dealer_hand = self.inst[source].dealer_hand
        return (result[1], f"Your hand is: {str(self.inst[source].player_hand)} \n Dealer's hand is: {str(dealer_hand)} \n {result[0]}")
                    

    async def do_clear(self, message: Message) -> str:
        if message.source.startswith('+'):
            source = message.source[1:]
        else:
            source = message.source
        self.inst.pop(source)
        return "Game cleared."
    async def do_c(self, message: Message) -> str:
        return await self.do_clear(message)

    async def blackjack_handler(self, message: Message, flag: str) -> str:
        if message.source.startswith('+'):
            source = message.source[1:]
        else:
            source = message.source

        if flag == "init":
            # if we've never seen this user before, create a new game
            if source not in self.inst:
                self.inst[source] = State(deck=self.make_deck(), player_hand=[], dealer_hand=[], player_score=0, dealer_score=0, discard=[], reset=False)
                self.inst[source].dealer_hand.append(self.inst[source].deck.pop())
                self.inst[source].player_hand.append(self.inst[source].deck.pop())
                self.inst[source].dealer_hand.append(self.inst[source].deck.pop().flip())
                self.inst[source].player_hand.append(self.inst[source].deck.pop())
                self.inst[source].player_score = self.calc_hand(self.inst[source].player_hand)
                self.inst[source].dealer_score = self.calc_hand(self.inst[source].dealer_hand)
                _outcome, text = self.calc_score(source)
                return text
            elif self.inst[source].discard != []:
                self.inst[source].dealer_hand.append(self.inst[source].deck.pop())
                self.inst[source].player_hand.append(self.inst[source].deck.pop())
                self.inst[source].dealer_hand.append(self.inst[source].deck.pop().flip())
                self.inst[source].player_hand.append(self.inst[source].deck.pop())
                self.inst[source].player_score = self.calc_hand(self.inst[source].player_hand)
                self.inst[source].dealer_score = self.calc_hand(self.inst[source].dealer_hand)
                _outcome, text = self.calc_score(source)
                return text

            return "Game already started"
        if source not in self.inst:
            return "Game not started"
        if flag == 'hit':
            self.inst[source].player_hand.append(self.inst[source].deck.pop())
        if self.inst[source].dealer_score < 17:
            self.inst[source].dealer_hand.append(self.inst[source].deck.pop())
        self.inst[source].player_score = self.calc_hand(self.inst[source].player_hand)
        self.inst[source].dealer_score = self.calc_hand(self.inst[source].dealer_hand)

        _outcome, text = self.calc_score(source)
        if self.inst[source].reset:
            self.inst[source].reset = False
            self.inst[source].discard.extend(self.inst[source].player_hand)
            self.inst[source].discard.extend(self.inst[source].dealer_hand)
            self.inst[source].player_hand = []
            self.inst[source].dealer_hand = []
            
        return text









if __name__ == "__main__":
    run_bot(BlackjackBot)