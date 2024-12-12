import torch
from src.model.chess_model import ChessNet
from src.model.training import ChessTrainer
from src.engine.chess_engine import ChessEngine
from src.data_processing.data_loader import ChessDataLoader
import os

def load_checkpoint(model, optimizer, checkpoint_path):
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
    data_loader = ChessDataLoader('data')

    checkpoint_path = 'checkpoint_latest.pth'
    start_epoch = 0
    if os.path.exists(checkpoint_path):
        print(f"Loading checkpoint from {checkpoint_path}")
        start_epoch = load_checkpoint(model, optimizer, checkpoint_path)

    batch_size = 32
    num_iterations = 100
    games_per_iteration = 50
    save_interval = 10

    print("Loading PGN data...")
    states, policies, values = data_loader.load_all_data()
    print(f"Loaded {len(states)} positions from PGN files")
    
    print("Training on PGN data...")
    total_loss = trainer.train_step(states, policies, values, batch_size)
    print(f"Initial PGN training loss: {total_loss:.4f}")

    # Continue with self-play training
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
        
        # Save checkpoint
        if iteration % save_interval == 0:
            torch.save({
                'epoch': iteration,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'loss': total_loss,
            }, f'checkpoint_{iteration}.pth')

if __name__ == "__main__":
    main()
