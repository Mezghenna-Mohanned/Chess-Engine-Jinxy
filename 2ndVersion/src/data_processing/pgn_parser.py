import chess.pgn
import numpy as np
from pathlib import Path

class PGNProcessor:
    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        
    def encode_board(self, board):
        # 12 planes for each piece type (6 white, 6 black)
        piece_planes = np.zeros((12, 8, 8), dtype=np.float32)
        
        for i in range(64):
            piece = board.piece_at(i)
            if piece is not None:
                color = int(piece.color)
                piece_idx = piece.piece_type - 1 + (6 * color)
                rank, file = divmod(i, 8)
                piece_planes[piece_idx][rank][file] = 1
                
        return piece_planes
    
    def process_game(self, game):
        states = []
        moves = []
        board = game.board()
        
        for move in game.mainline_moves():
            if board.turn == chess.BLACK:  # We only want positions where it's black's turn
                states.append(self.encode_board(board))
                moves.append(str(move))
            board.push(move)
            
        return states, moves
    
    def load_games(self):
        states = []
        moves = []
        
        for pgn_file in self.data_dir.glob("*.pgn"):
            with open(pgn_file) as f:
                while True:
                    game = chess.pgn.read_game(f)
                    if game is None:
                        break
                    game_states, game_moves = self.process_game(game)
                    states.extend(game_states)
                    moves.extend(game_moves)
                    
        return np.array(states), np.array(moves)
