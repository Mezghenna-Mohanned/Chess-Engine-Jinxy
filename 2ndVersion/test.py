import torch
from src.model.chess_model import ChessNet
from src.engine.chess_engine import ChessEngine
import chess

def load_checkpoint(model, optimizer, checkpoint_path):
    checkpoint = torch.load(checkpoint_path)
    model.load_state_dict(checkpoint['model_state_dict'])
    optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    start_epoch = checkpoint['epoch']
    return start_epoch

def play_game():
    model = ChessNet(device='cpu')
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    checkpoint_path = 'checkpoint_110.pth'
    load_checkpoint(model, optimizer, checkpoint_path)

    engine = ChessEngine(model, device='cpu')
    board = chess.Board()

    while not board.is_game_over():
        print(board)
        if board.turn == chess.BLACK:
            move = engine.get_best_move(board)
            print(f"Engine plays: {move}")
            board.push(move)
        else:
            user_input = input("Enter your move (e.g., e2e4): ")
            move = chess.Move.from_uci(user_input)
            if move in board.legal_moves:
                board.push(move)
            else:
                print("Illegal move! Try again.")

    print("Game Over!")
    print("Result:", board.result())

if __name__ == "__main__":
    play_game()
