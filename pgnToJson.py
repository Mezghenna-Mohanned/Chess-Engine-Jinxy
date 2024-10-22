import json
import chess.pgn
from collections import defaultdict
from io import StringIO

def add_move_to_tree(move_tree, move_sequence):
    current_level = move_tree
    for move in move_sequence:
        if move not in current_level:
            current_level[move] = {}
        current_level = current_level[move]

def pgn_to_move_tree(pgn_text):
    move_tree = {}
    pgn_io = StringIO(pgn_text)
    while True:
        game = chess.pgn.read_game(pgn_io)
        if game is None:
            break
        board = game.board()
        move_sequence = []
        for move in game.mainline_moves():
            move_sequence.append(board.san(move))
            board.push(move)
        board = game.board()
        uci_sequence = []
        for move in game.mainline_moves():
            uci_move = move.uci()
            uci_sequence.append(uci_move)
            board.push(move)
        add_move_to_tree(move_tree, uci_sequence)
    return move_tree

pgn_data = """
"""

move_tree = pgn_to_move_tree(pgn_data)
with open('move_tree.json', 'w') as json_file:
    json.dump(move_tree, json_file, indent=4)
