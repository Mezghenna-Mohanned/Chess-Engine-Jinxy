# train_model.py

import os
import chess.pgn
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
import json
from tqdm import tqdm

DATA_DIR = 'data'
MODEL_SAVE_PATH = 'models/best_move_model.pth'
LABELS_SAVE_PATH = 'models/labels_mapping.json'
BATCH_SIZE = 64
EPOCHS = 10
LEARNING_RATE = 0.001
INPUT_SIZE = 832
HIDDEN_SIZES = [1024, 512, 256]
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

os.makedirs('models', exist_ok=True)

PIECE_TO_INDEX = {
    'P': 0, 'N': 1, 'B': 2, 'R': 3, 'Q': 4, 'K': 5,
    'p': 6, 'n': 7, 'b': 8, 'r': 9, 'q': 10, 'k': 11
}

class ChessDataset(Dataset):
    def __init__(self, data_dir, move_to_int, int_to_move):
        self.features = []
        self.labels = []
        self.move_to_int = move_to_int
        self.int_to_move = int_to_move
        self._load_data(data_dir)
    
    def _load_data(self, data_dir):
        pgn_files = [f for f in os.listdir(data_dir) if f.endswith('.pgn')]
        for pgn_file in pgn_files:
            pgn_path = os.path.join(data_dir, pgn_file)
            with open(pgn_path, 'r') as f:
                while True:
                    game = chess.pgn.read_game(f)
                    if game is None:
                        break
                    board = game.board()
                    for move in game.mainline_moves():
                        fen = board.fen()
                        feature = self.fen_to_features(fen)
                        move_uci = move.uci()
                        if move_uci not in self.move_to_int:
                            continue
                        label = self.move_to_int[move_uci]
                        self.features.append(feature)
                        self.labels.append(label)
                        board.push(move)
    
    def fen_to_features(self, fen):
        board = chess.Board(fen)
        feature = np.zeros((8, 8, 13), dtype=np.float32)
        for square, piece in board.piece_map().items():
            row = 7 - (square // 8)
            col = square % 8
            piece_idx = PIECE_TO_INDEX[piece.symbol()]
            feature[row, col, piece_idx] = 1
        active_color = 1 if board.turn == chess.WHITE else 0
        feature[:, :, 12] = active_color
        return feature.flatten()
    
    def __len__(self):
        return len(self.labels)
    
    def __getitem__(self, idx):
        return torch.tensor(self.features[idx], dtype=torch.float32), torch.tensor(self.labels[idx], dtype=torch.long)

class ChessMovePredictor(nn.Module):
    def __init__(self, input_size=832, hidden_sizes=[1024, 512, 256], output_size=1439):
        super(ChessMovePredictor, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_sizes[0])
        self.relu1 = nn.ReLU()
        self.fc2 = nn.Linear(hidden_sizes[0], hidden_sizes[1])
        self.relu2 = nn.ReLU()
        self.fc3 = nn.Linear(hidden_sizes[1], hidden_sizes[2])
        self.relu3 = nn.ReLU()
        self.output = nn.Linear(hidden_sizes[2], output_size)
    
    def forward(self, x):
        x = self.relu1(self.fc1(x))
        x = self.relu2(self.fc2(x))
        x = self.relu3(self.fc3(x))
        x = self.output(x)
        return x

def build_move_mappings(data_dir):
    move_set = set()
    pgn_files = [f for f in os.listdir(data_dir) if f.endswith('.pgn')]
    for pgn_file in pgn_files:
        pgn_path = os.path.join(data_dir, pgn_file)
        with open(pgn_path, 'r') as f:
            while True:
                game = chess.pgn.read_game(f)
                if game is None:
                    break
                board = game.board()
                for move in game.mainline_moves():
                    move_set.add(move.uci())
                    board.push(move)
    move_list = sorted(list(move_set))
    move_to_int = {move: idx for idx, move in enumerate(move_list)}
    int_to_move = {idx: move for move, idx in move_to_int.items()}
    return move_to_int, int_to_move

def main():
    print("Building move mappings...")
    move_to_int, int_to_move = build_move_mappings(DATA_DIR)
    with open(LABELS_SAVE_PATH, 'w') as f:
        json.dump({'move_to_int': move_to_int, 'int_to_move': int_to_move}, f)
    print(f"Saved move mappings to {LABELS_SAVE_PATH}")
    
    print("Loading dataset...")
    dataset = ChessDataset(DATA_DIR, move_to_int, int_to_move)
    dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)
    print(f"Total samples: {len(dataset)}")
    
    print("Initializing model...")
    model = ChessMovePredictor(input_size=INPUT_SIZE, hidden_sizes=HIDDEN_SIZES, output_size=len(move_to_int))
    model.to(DEVICE)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    
    print("Starting training...")
    for epoch in range(EPOCHS):
        model.train()
        running_loss = 0.0
        for inputs, labels in tqdm(dataloader, desc=f"Epoch {epoch+1}/{EPOCHS}"):
            inputs, labels = inputs.to(DEVICE), labels.to(DEVICE)
            
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item() * inputs.size(0)
        epoch_loss = running_loss / len(dataset)
        print(f"Epoch {epoch+1}/{EPOCHS}, Loss: {epoch_loss:.4f}")

    torch.save(model.state_dict(), MODEL_SAVE_PATH)
    print(f"Training complete. Model saved to {MODEL_SAVE_PATH}")

if __name__ == "__main__":
    main()
