# predict_move.py

import torch
import numpy as np
import json
import chess
from utils import algebraic_to_square, square_to_algebraic
from train_model import ChessMovePredictor

class MovePredictor:
    def __init__(self, model_path='models/best_move_model.pth', labels_path='models/labels_mapping.json'):
        with open(labels_path, 'r') as f:
            mappings = json.load(f)
        self.move_to_int = {k: v for k, v in mappings['move_to_int'].items()}
        self.int_to_move = {int(k): v for k, v in mappings['int_to_move'].items()}
        self.num_moves = len(self.int_to_move)

        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Using device: {self.device}")

        self.model = ChessMovePredictor(input_size=832, hidden_sizes=[1024, 512, 256], output_size=self.num_moves)
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()

    def fen_to_features(self, fen):
        """
        Converts a FEN string to a numerical feature array, including active color.
        """
        board = chess.Board(fen)
        feature = np.zeros((8, 8, 13), dtype=np.float32)  # 12 for pieces + 1 for active color
        piece_to_index = {
            'P': 0, 'N': 1, 'B': 2, 'R': 3, 'Q': 4, 'K': 5,
            'p': 6, 'n': 7, 'b': 8, 'r': 9, 'q': 10, 'k': 11
        }
        for square, piece in board.piece_map().items():
            row = 7 - (square // 8)
            col = square % 8
            piece_idx = piece_to_index[piece.symbol()]
            feature[row, col, piece_idx] = 1
        active_color = 1 if board.turn == chess.WHITE else 0
        feature[:, :, 12] = active_color
        return feature.flatten()

    def predict_move(self, fen, legal_moves):
        """
        Predicts the best move given the current board state, ensuring it's legal.

        Parameters:
        - fen (str): FEN string of the current board state.
        - legal_moves (list of Move objects): List of currently legal moves.

        Returns:
        - str or None: Predicted move in UCI format, or None if prediction fails.
        """
        features = self.fen_to_features(fen)
        features = torch.tensor(features, dtype=torch.float32).unsqueeze(0).to(self.device)

        with torch.no_grad():
            outputs = self.model(features)
            probabilities = torch.softmax(outputs, dim=1)
            top_move_idx = torch.argmax(probabilities, dim=1).item()
            predicted_move = self.int_to_move.get(top_move_idx, None)

        # tvalidi if the predicted move is legal
        if predicted_move and self.is_move_legal(predicted_move, legal_moves):
            return predicted_move
        else:
            return None

    def is_move_legal(self, move_str, legal_moves):
        for move in legal_moves:
            if str(move) == move_str:
                return True
        return False
