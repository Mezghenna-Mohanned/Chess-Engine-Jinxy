import os
import chess.pgn
import numpy as np
from .state_encoder import StateEncoder

class ChessDataLoader:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.encoder = StateEncoder()
        
    def load_all_data(self):
        states = []
        policies = []
        values = []
        
        # Load player games
        player_data = self._load_directory(os.path.join(self.data_dir, 'players'))
        states.extend(player_data[0])
        policies.extend(player_data[1])
        values.extend(player_data[2])
        
        # Load opening data
        opening_data = self._load_directory(os.path.join(self.data_dir, 'openings'))
        states.extend(opening_data[0])
        policies.extend(opening_data[1])
        values.extend(opening_data[2])
        
        # Load general games
        games_data = self._load_directory(os.path.join(self.data_dir, 'games'))
        states.extend(games_data[0])
        policies.extend(games_data[1])
        values.extend(games_data[2])
        
        return np.array(states), np.array(policies), np.array(values)
    
    def _load_directory(self, directory):
        states = []
        policies = []
        values = []
        
        for filename in os.listdir(directory):
            if filename.endswith('.pgn'):
                pgn_path = os.path.join(directory, filename)
                with open(pgn_path) as pgn_file:
                    while True:
                        game = chess.pgn.read_game(pgn_file)
                        if game is None:
                            break
                            
                        game_states, game_policies, game_value = self._process_game(game)
                        states.extend(game_states)
                        policies.extend(game_policies)
                        values.extend([game_value] * len(game_states))
                        
        return states, policies, values
    
    def _process_game(self, game):
        states = []
        policies = []
        
        board = game.board()
        for move in game.mainline_moves():
            if board.turn == chess.BLACK:
                states.append(self.encoder.encode_board(board))
                policy = np.zeros(4672)
                policy[self.encoder.move_to_index(move)] = 1
                policies.append(policy)
            board.push(move)
            
        result = game.headers.get("Result", "*")
        if result == "1-0":
            value = -1
        elif result == "0-1":
            value = 1
        else:
            value = 0
            
        return states, policies, value
