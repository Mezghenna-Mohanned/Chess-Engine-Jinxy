import chess
import numpy as np

class StateEncoder:
    def __init__(self):
        self.piece_to_index = {
            'P': 0, 'N': 1, 'B': 2, 'R': 3, 'Q': 4, 'K': 5,
            'p': 6, 'n': 7, 'b': 8, 'r': 9, 'q': 10, 'k': 11
        }

    def encode_board(self, board):
        state = np.zeros((12, 8, 8), dtype=np.float32)

        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece is not None:
                rank, file = divmod(square, 8)
                piece_index = self.piece_to_index[piece.symbol()]
                state[piece_index, rank, file] = 1

        return state

    def decode_move(self, move_probs, board):
        legal_moves = list(board.legal_moves)
        move_probs = move_probs.reshape(-1)
        legal_move_probs = [move_probs[self.move_to_index(move)] for move in legal_moves]
        selected_move = legal_moves[np.argmax(legal_move_probs)]
        return selected_move
    
    
    def move_to_index(self, move):
        """Convert a chess move to a policy index (0-4095)"""
        from_square = move.from_square
        to_square = move.to_square
        return from_square * 64 + to_square

    def index_to_move(self, index):
        """Convert a policy index back to a chess move"""
        from_square = index // 64
        to_square = index % 64
        return chess.Move(from_square, to_square)
