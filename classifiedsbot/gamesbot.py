import random
from typing import List, Dict
from games.card import Card
from forest.core import Bot, Message, run_bot
# from forest.pdictng import aPersistDict




class State:
    def __init__(self, deck: List[Card], dealer_hand: List[Card], player_hand: List[Card]):
        self.deck = deck
        self.player_hand = player_hand
        self.dealer_hand = dealer_hand
    # player_bet: int



class BlackjackBot(Bot):
    def __init__(self) -> None:
        self.instances: Dict = {}
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

    def calc_hand(hand: List[List[Card]], _) -> int:

        """Calculates the sum of the card values and accounts for aces"""
        non_aces = [c for c in hand if c.symbol != 'A']
        aces = [c for c in hand if c.symbol == 'A']
        sum = 0
        for card in non_aces:
            if not card.down:
                if card.symbol in 'JQK': sum += 10
                else: sum += card.value
        for card in aces:
            if not card.down:
                if sum <= 10: sum += 11
                else: sum += 1
        return sum

    def make_deck(self) -> List[Card]:
        deck = [Card(suit, num) for num in range(2,15) for suit in Card.suits]
        random.shuffle(deck)
        return deck

    async def do_b(self, message: Message) -> str:
        return await self.blackjack_handler(message, flag = "init")
    async def do_blackjack(self, message: Message) -> str:
        return await self.blackjack_handler(message, flag = "init")
    async def do_hit(self, message: Message) -> str:
        return await self.blackjack_handler(message, flag = "hit")
    async def do_stand(self, message: Message) -> str:
        return await self.blackjack_handler(message=message, flag = "stand")

    async def blackjack_handler(self, message: Message, flag: str) -> str:
        if message.source.startswith('+'):
            source = message.source[1:]
        else:
            source = message.source
        if flag == "init":
            if source not in self.instances:
                self.instances[source] = State(deck=self.make_deck(), player_hand=[], dealer_hand=[])

                self.instances[source].player_hand.append(self.instances[source].deck.pop())
                self.instances[source].dealer_hand.append(self.instances[source].deck.pop())

                self.instances[source].player_hand.append(self.instances[source].deck.pop())
                self.instances[source].dealer_hand.append(self.instances[source].deck.pop().flip())
                print(self.instances[source].player_hand[0].symbol)

                player_score = self.calc_hand(self.instances[source].player_hand)
                dealer_score = self.calc_hand(self.instances[source].dealer_hand)

                # if both player and dealer have 21
                if player_score == 21 and dealer_score == 21:
                    return "You both have 21. It's a tie."
                # if player has 21
                elif player_score == 21:
                    return "You have 21. You win!"
                # if dealer has 21 and player does not
                elif dealer_score == 21:
                    return "Dealer has 21. You lose."
                # if neither player nor dealer has 21
                else:
                    return f"Your hand is: {str(self.instances[source].player_hand)} for a score of {str(player_score)} \n" \
                           f"Dealer's hand is: {str(self.instances[source].dealer_hand)} for a score of {str(dealer_score)} \n" \
                           "You can hit or stand."
                # print(dir(self.instances[source].dealer_hand))
                # return "Your hand: " + str(self.instances[source].player_hand) + "\n" + "Dealer's hand: " + str(self.instances[source].dealer_hand)
            return "Game already started"
        elif flag == "hit":
            if source not in self.instances:
                return "Game not started"
            self.instances[source].player_hand.append(self.instances[source].deck.pop())
            self.instances[source].dealer_hand.append(self.instances[source].deck.pop())

            player_score = self.calc_hand(self.instances[source].player_hand)
            dealer_score = self.calc_hand(self.instances[source].dealer_hand)
            return "Player hit"
        elif flag == "stand":
            if source not in self.instances:
                return "Game not started"
            # if self.instances[source].dealer_hand
                # self.instances[source].dealer_hand.append(self.instances[source].deck.pop())








if __name__ == "__main__":
    run_bot(BlackjackBot)