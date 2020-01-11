"""
Jeremy Storring, JNS855, 11218129
CMPT 317: A4Q5
Michael Horsch
"""

from Game import Game
import Players
import AlphaBetaDL
import sys

# create the game, and the initial state
game = Game(5, depth=1)
state = game.initial_state()
current_player = Players.VerboseComputer(game, AlphaBetaDL.AlphaBeta(game))
game = Game(5, depth=1)
other_player = Players.VerboseComputer(game, AlphaBetaDL.AlphaBeta(game))

# play the game
while not game.is_terminal(state):
    choice = current_player.ask_move(state)
    state = game.result(state, choice)
    current_player, other_player = other_player, current_player

game.congratulate(state)
winner = state.cachedWinner
if state.cachedWinner:
    winner = "Rebels"
elif not state.cachedWinner:
    winner = "Sith"
else:
    winner = "draw"

game = Game(5, depth=2)
state = game.initial_state()

current_player = Players.VerboseComputer(game, AlphaBetaDL.AlphaBeta(game))

game = Game(5, depth=2)
other_player = Players.VerboseComputer(game, AlphaBetaDL.AlphaBeta(game))

# play the game
while not game.is_terminal(state):
    state.display()
    choice = current_player.ask_move(state)
    state = game.result(state, choice)
    current_player, other_player = other_player, current_player

state.display()
game.congratulate(state)
if state.cachedWinner:
    winner2 = "Rebels"
elif not state.cachedWinner:
    winner2 = "Sith"
else:
    winner2 = "draw"

print("-------------------------------------------------")
print("|Player 1 | Depth | Player 2 | Depth |   Outcome  |")
print("|---------|-------|----------|-------|------------|")
print("| A4Q3.py |   1   |  A4Q2.py |   1   |   " + winner + "   |")
print("|---------|-------|----------|-------|------------|")
print("| A4Q3.py |   2   |  A4Q2.py |   2   |   " + winner2 + "   |")
print("---------------------------------------------------")
# eof