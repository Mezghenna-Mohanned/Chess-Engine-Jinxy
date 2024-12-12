import chess
import torch
import numpy as np

class ChessEngine:
    def __init__(self, model, device='cuda'):
        self.model = model.to(device)
        self.device = device
        
    def get_move(self, board, temperature=1.0):
        self.model.eval()
        state = self.encode_board(board).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            policy, value = self.model(state)
            
        # Filter legal moves
        legal_moves = [str(move) for move in board.legal_moves]
        policy = policy.exp().cpu().numpy()[0]
        
        # Apply temperature
        policy = np.power(policy, 1/temperature)
        policy = policy / np.sum(policy)
        
        # Select move
        move_idx = np.random.choice(len(legal_moves), p=policy)
        return chess.Move.from_uci(legal_moves[move_idx])
    
    def self_play(self, num_games=100):
        games_data = []
        
        for game_idx in range(num_games):
            board = chess.Board()
            states = []
            policies = []
            
            while not board.is_game_over():
                if board.turn == chess.BLACK:
                    move = self.get_move(board)
                    states.append(self.encode_board(board))
                    policy = np.zeros(4672)  # Total possible moves
                    policy[self.move_to_index(move)] = 1
                    policies.append(policy)
                else:
                    # Random move for white
                    moves = list(board.legal_moves)
                    move = np.random.choice(moves)
                board.push(move)
            
            # Get game result
            result = board.result()
            value = 1 if result == "0-1" else (-1 if result == "1-0" else 0)
            values = [value] * len(states)
            
            games_data.append((states, policies, values))
            
        return games_data
