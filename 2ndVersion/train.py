import torch
from src.model.chess_model import ChessNet
from src.model.training import ChessTrainer
from src.engine.chess_engine import ChessEngine
import os

def load_checkpoint(model, optimizer, checkpoint_path):
    """Load model and optimizer state from a checkpoint."""
    checkpoint = torch.load(checkpoint_path)
    model.load_state_dict(checkpoint['model_state_dict'])
    optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    start_epoch = checkpoint['epoch']
    return start_epoch

def main():
    device = 'cpu'
    print(f"Using device: {device}")

    model = ChessNet(device=device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    trainer = ChessTrainer(model, device=device)
    engine = ChessEngine(model, device=device)

    checkpoint_path = 'checkpoint_50.pth'
    start_epoch = 0

    if os.path.exists(checkpoint_path):
        print(f"Loading checkpoint from {checkpoint_path}")
        start_epoch = load_checkpoint(model, optimizer, checkpoint_path)

    batch_size = 32
    num_iterations = 100
    games_per_iteration = 50
    save_interval = 10

    for iteration in range(start_epoch, num_iterations + start_epoch):
        print(f"Starting iteration {iteration}")

        games_data = engine.self_play(num_games=games_per_iteration)

        states = []
        policies = []
        values = []
        for game_states, game_policies, game_values in games_data:
            states.extend(game_states)
            policies.extend(game_policies)
            values.extend(game_values)

        total_loss = trainer.train_step(states, policies, values, batch_size)
        print(f"Iteration {iteration}, Loss: {total_loss:.4f}")

        if iteration % save_interval == 0:
            torch.save({
                'epoch': iteration,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'loss': total_loss,
            }, f'checkpoint_{iteration}.pth')

if __name__ == "__main__":
    main()
