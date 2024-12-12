from src.model.chess_model import ChessNet
from src.model.training import ChessTrainer
from src.engine.chess_engine import ChessEngine
import torch

def main():
    # Set device
    device = 'cpu'
    print(f"Using device: {device}")
    
    # Initialize components with smaller network size
    model = ChessNet(device=device)
    trainer = ChessTrainer(model, device=device, learning_rate=0.001)
    engine = ChessEngine(model, device=device)
    
    # Training configuration
    batch_size = 32  # Smaller batch size for CPU
    num_epochs = 10
    games_per_iteration = 50  # Reduced number of self-play games
    
    # Training loop
    for iteration in range(100):
        print(f"Starting iteration {iteration}")
        
        # Generate games through self-play
        games_data = engine.self_play(num_games=games_per_iteration)
        
        # Train on new games
        for epoch in range(num_epochs):
            total_loss = trainer.train_step(
                games_data['states'],
                games_data['policies'],
                games_data['values'],
                batch_size=batch_size
            )
            print(f"Epoch {epoch}, Loss: {total_loss:.4f}")
            
        # Save model periodically
        if iteration % 10 == 0:
            torch.save(model.state_dict(), f'model_iter_{iteration}.pth')

if __name__ == "__main__":
    main()
