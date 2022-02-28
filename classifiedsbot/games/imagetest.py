from PIL import Image
import os
import random
from pathlib import Path
from card import Card
ABS_PATH = Path(os.getcwd())
# ABS_PATH = "/home/olivia/forest/classifiedsbot/"
# COG_FOLDER = os.path.join(ABS_PATH, 'cogs/')
from typing import List, Tuple, Union

# class Card:
#     suits = ["clubs", "diamonds", "hearts", "spades"]
#     def __init__(self, suit: str, value: int, down=False):
#         self.suit = suit
#         self.value = value
#         self.down = down
#         self.symbol = self.name[0].upper()

#     @property
#     def name(self) -> str:
#         """The name of the card value."""
#         if self.value <= 10: return str(self.value)
#         else: return {
#             11: 'jack',
#             12: 'queen',
#             13: 'king',
#             14: 'ace',
#         }[self.value]

#     @property
#     def image(self):
#         return (
#             f"{self.symbol if self.name != '10' else '10'}"\
#             f"{self.suit[0].upper()}.png" \
#             if not self.down else "red_back.png"
#         )

#     def flip(self):
#         self.down = not self.down
#         return self

#     def __str__(self) -> str:
#         return f'{self.name.title()} of {self.suit.title()}'

#     def __repr__(self) -> str:
#         return str(self)

def hand_to_images(hand: List[Card]) -> List[Image.Image]:
    return ([
        Image.open(os.path.join(ABS_PATH, 'classifiedsbot/games/cards/', card.image))
        for card in hand
    ])


def center(*hands: Tuple[Image.Image]) -> Image.Image:
    """Creates blackjack table with cards placed"""
    bg: Image.Image = Image.open(
        os.path.join(ABS_PATH, 'classifiedsbot/games/', 'table.png')
    )
    bg_center_x = bg.size[0] // 2
    bg_center_y = bg.size[1] // 2

    img_w = hands[0][0].size[0]
    img_h = hands[0][0].size[1]

    start_y = bg_center_y - (((len(hands)*img_h) + \
        ((len(hands) - 1) * 15)) // 2)
    for hand in hands:
        start_x = bg_center_x - (((len(hand)*img_w) + \
            ((len(hand) - 1) * 10)) // 2)
        for card in hand:
            bg.alpha_composite(card, (start_x, start_y))
            start_x += img_w + 10
        start_y += img_h + 15
    return bg

def output(name, *hands: Tuple[List[Card]]) -> None:
    center(*map(hand_to_images, hands)).save(f'{name}.png')
    return f"{ABS_PATH}/{name}.png"

def GenerateImage(name: str, hands: List[List[Card]]) -> None:
    output(name, *hands)

if __name__ == "__main__":   
    deck = [Card(suit, num) for num in range(2,15) for suit in Card.suits]
    random.shuffle(deck)
    player_hand: List[Card] = []
    dealer_hand: List[Card] = []

    player_hand.append(deck.pop())
    dealer_hand.append(deck.pop())
    player_hand.append(deck.pop())
    dealer_hand.append(deck.pop().flip())
    print(output("testhand", player_hand, dealer_hand))