import chess
import torch
from ..model.chess_model import ChessNet
from ..data_processing.state_encoder import StateEncoder
import numpy as np

class ChessEngine:
    def __init__(self, model, device='cpu'):
        self.model = model.to(device)
        self.device = device
        self.encoder = StateEncoder()

    def get_best_move(self, board, temperature=1.0):
        state = self.encoder.encode_board(board)
        state = torch.FloatTensor(state).unsqueeze(0).to(self.device)

        with torch.no_grad():
            policy, value = self.model(state)
            
        # Get move probabilities
        policy = policy.exp().cpu().numpy()[0]
        
        # Filter legal moves
        legal_moves = list(board.legal_moves)
        legal_move_probs = np.zeros(len(legal_moves))
        
        for i, move in enumerate(legal_moves):
            idx = self.encoder.move_to_index(move)
            if idx < len(policy):
                legal_move_probs[i] = policy[idx]
        
        # Apply temperature
        if temperature != 1.0:
            legal_move_probs = np.power(legal_move_probs, 1/temperature)
        
        # Normalize probabilities
        legal_move_probs = legal_move_probs / np.sum(legal_move_probs)
        
        # Select move
        selected_move = np.random.choice(legal_moves, p=legal_move_probs)
        return selected_move


    def play_game(self, opponent_func, max_moves=200):
        board = chess.Board()
        for _ in range(max_moves):
            if board.turn == chess.BLACK:
                move = self.get_best_move(board)
            else:
                move = opponent_func(board)

            board.push(move)
            if board.is_game_over():
                break

        return board.result()

    def self_play(self, num_games=50):
        games_data = []

        for _ in range(num_games):
            board = chess.Board()
            states = []
            policies = []
            
            while not board.is_game_over():
                state = self.encoder.encode_board(board)
                move = self.get_best_move(board, temperature=1.0)
                
                policy = np.zeros(4672)  # Total possible moves
                policy[self.encoder.move_to_index(move)] = 1
                
                states.append(state)
                policies.append(policy)
                board.push(move)

            result = board.result()
            value = 1 if result == "0-1" else (-1 if result == "1-0" else 0)
            values = [value] * len(states)
            
            games_data.append((states, policies, values))

        return games_data
