import random
from forest.core import Bot, Message, run_bot
from typing import Dict


class GuessBot(Bot):
    def __init__(self) -> None:
        self.instances: Dict = {}
        super().__init__()

    async def do_newgame(self, message: Message) -> str:
        "start a new guessing game with numbers between 0 and 9 inclusive."
        
        if message.source.startswith('+'):
            source = message.source[1:]
        else:
            source = message.source
        if source in self.instances:
            return "You have to finish your current game first"
        guesses = 0
        self.instances[source] = [random.randint(0, 9), guesses]
        return f"New game started. Guess a number between 0 and 9 with 'guess x'. for debug purposes, the number is {self.instances[source][0]}"

    async def do_guess(self, message: Message) -> str:
        "send a guess to the current game, ie 'guess 3'"
        if message.source.startswith('+'):
            source = message.source[1:]
        else:
            source = message.source
        if source in self.instances:
            guess = int(message.text)
            self.instances[source][1] += 1
            if guess == self.instances[source][0]:
                self.instances.pop(source)
                return "You win!"
            return "Wrong guess"
        else:
            return "You have to start a new game first"

    async def do_games(self, _: Message) -> str:
        "list all active games"
        return str([f"source user: {key}, \ngame number: {self.instances[key][0]}, guess count: {self.instances[key][1]}" for key in self.instances])

if __name__ == "__main__":
    run_bot(GuessBot)