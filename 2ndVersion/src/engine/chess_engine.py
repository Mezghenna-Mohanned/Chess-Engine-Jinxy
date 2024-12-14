import torch
from ..model.chess_model import ChessNet
from ..data_processing.state_encoder import StateEncoder
import numpy as np
from .Evaluator import Evaluator

class ChessEngine:
    def __init__(self, model, device='cpu', evaluator=None):
        self.model = model.to(device)
        self.device = device
        self.encoder = StateEncoder()
        self.evaluator = evaluator or Evaluator()

    def get_best_move(self, board, temperature=0.8):
        print("Encoding board state for neural network...")
        state = self.encoder.encode_board(board)
        state = torch.FloatTensor(state).unsqueeze(0).to(self.device)

        # is using neural network evaluation
        with torch.no_grad():
            policy, value = self.model(state)

        print("calculating the best move...")
        bot_move = self.evaluator.get_best_move(board)
        eval = self.evaluator.evaluate_position(board)

        print(f"best move: {bot_move}, evaluation: {eval}")

        #combine evaluations
        policy = policy.exp().cpu().numpy()[0]
        legal_moves = list(board.legal_moves)
        legal_move_probs = np.zeros(len(legal_moves))

        for i, move in enumerate(legal_moves):
            if move == bot_move:
                legal_move_probs[i] = 0.7
            else:
                idx = self.encoder.move_to_index(move)
                if idx < len(policy):
                    legal_move_probs[i] = 0.3 * policy[idx]

        if temperature != 1.0:
            legal_move_probs = np.power(legal_move_probs, 1 / temperature)
        legal_move_probs /= np.sum(legal_move_probs)

        selected_move = np.random.choice(legal_moves, p=legal_move_probs)
        print(f"selected move: {selected_move}")
        return selected_move
