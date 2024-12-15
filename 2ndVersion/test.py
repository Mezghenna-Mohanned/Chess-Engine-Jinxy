import torch
from src.model.chess_model import ChessNet
from src.engine.chess_engine import ChessEngine
from src.engine.Evaluator import Evaluator
import chess

def load_checkpoint(model, optimizer, checkpoint_path):
    checkpoint = torch.load(checkpoint_path)
    model.load_state_dict(checkpoint['model_state_dict'])
    optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    start_epoch = checkpoint['epoch']
    print(f"Loaded checkpoint from epoch {start_epoch}")
    return start_epoch

def play_game():
    device = 'cpu'
    model = ChessNet(device=device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    evaluator = Evaluator(
        elo_rating=1700
    )

    checkpoint_path = 'checkpoint_50.pth' # now up to checkpoint_110.pth but not pushed
    load_checkpoint(model, optimizer, checkpoint_path)

    engine = ChessEngine(model, device=device, evaluator=evaluator)
    board = chess.Board()

    while not board.is_game_over():
        print(board)
        if board.turn == chess.BLACK:
            print("Engine's turn...")
            move = engine.get_best_move(board)
            print(f"Engine plays: {move}")
            board.push(move)
        else:
            user_input = input("Enter your move (e.g., e2e4): ")
            try:
                move = chess.Move.from_uci(user_input)
                if move in board.legal_moves:
                    board.push(move)
                else:
                    print("Illegal move! Try again.")
            except ValueError:
                print("Invalid move format! Please use format like 'e2e4'")

    print("Game Over!")
    print("Result:", board.result())

if __name__ == "__main__":
    play_game()
