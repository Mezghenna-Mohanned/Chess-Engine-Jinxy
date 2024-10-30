import chess.pgn
import pandas as pd
import numpy as np
import os
from tqdm import tqdm
import json
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader

class ChessDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.long)

    def __len__(self):
        return len(self.y)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

class ChessMovePredictor(nn.Module):
    def __init__(self, input_size, hidden_sizes, output_size):
        super(ChessMovePredictor, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_sizes[0])
        self.relu1 = nn.ReLU()
        self.dropout1 = nn.Dropout(0.3)
        self.fc2 = nn.Linear(hidden_sizes[0], hidden_sizes[1])
        self.relu2 = nn.ReLU()
        self.dropout2 = nn.Dropout(0.3)
        self.fc3 = nn.Linear(hidden_sizes[1], hidden_sizes[2])
        self.relu3 = nn.ReLU()
        self.dropout3 = nn.Dropout(0.3)
        self.output = nn.Linear(hidden_sizes[2], output_size)

    def forward(self, x):
        out = self.fc1(x)
        out = self.relu1(out)
        out = self.dropout1(out)
        out = self.fc2(out)
        out = self.relu2(out)
        out = self.dropout2(out)
        out = self.fc3(out)
        out = self.relu3(out)
        out = self.dropout3(out)
        out = self.output(out)
        return out

def parse_pgn_files(pgn_directory):
    """
    Parses all PGN files in the specified directory and extracts games.

    Parameters:
    - pgn_directory (str): Path to the directory containing PGN files.

    Returns:
    - List[chess.pgn.Game]: A list of parsed chess games.
    """
    games = []
    for filename in os.listdir(pgn_directory):
        if filename.endswith('.pgn'):
            filepath = os.path.join(pgn_directory, filename)
            with open(filepath, encoding='utf-8') as pgn:
                while True:
                    game = chess.pgn.read_game(pgn)
                    if game is None:
                        break
                    games.append(game)
    return games

def extract_moves(games, max_moves_per_game=100):
    """
    Extracts board states and moves from parsed games.

    Parameters:
    - games (List[chess.pgn.Game]): List of parsed chess games.
    - max_moves_per_game (int): Maximum number of moves to extract from each game.

    Returns:
    - List[Dict]: A list of dictionaries containing FEN strings and corresponding moves.
    """
    data = []
    for game in tqdm(games, desc="Processing Games"):
        board = game.board()
        move_count = 0
        for move in game.mainline_moves():
            if move_count >= max_moves_per_game:
                break
            fen_before = board.fen()
            board.push(move)
            move_uci = move.uci()
            data.append({
                'fen': fen_before,
                'move': move_uci
            })
            move_count += 1
    return data

def fen_to_features(fen):
    """
    Converts a FEN string to a numerical feature array.

    Parameters:
    - fen (str): Forsyth-Edwards Notation string representing the board state.

    Returns:
    - np.ndarray: Flattened feature array representing the board.
    """
    board = chess.Board(fen)
    feature = np.zeros((8, 8, 12), dtype=np.float32)
    piece_to_index = {
        'P': 0, 'N': 1, 'B': 2, 'R': 3, 'Q': 4, 'K': 5,
        'p': 6, 'n': 7, 'b': 8, 'r': 9, 'q': 10, 'k': 11
    }
    for square, piece in board.piece_map().items():
        row = 7 - (square // 8)
        col = square % 8
        piece_idx = piece_to_index[piece.symbol()]
        feature[row, col, piece_idx] = 1
    return feature.flatten()

def prepare_dataset(data):
    """
    Converts the dataset into features and labels suitable for model training.

    Parameters:
    - data (List[Dict]): List of dictionaries with 'fen' and 'move' keys.

    Returns:
    - Tuple[np.ndarray, np.ndarray, LabelEncoder]: Features, encoded labels, and the label encoder.
    """
    features = []
    labels = []
    for entry in tqdm(data, desc="Converting FEN to Features"):
        features.append(fen_to_features(entry['fen']))
        labels.append(entry['move'])

    X = np.array(features)
    y = np.array(labels)

    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)

    return X, y_encoded, label_encoder

def save_label_mapping(label_encoder, filepath):
    """
    Saves the label encoder mapping to a JSON file.

    Parameters:
    - label_encoder (LabelEncoder): Fitted label encoder.
    - filepath (str): Path to save the JSON file.
    """
    move_to_int = {move: int(idx) for move, idx in zip(label_encoder.classes_, label_encoder.transform(label_encoder.classes_))}
    int_to_move = {str(idx): move for move, idx in move_to_int.items()}
    with open(filepath, 'w') as f:
        json.dump({'move_to_int': move_to_int, 'int_to_move': int_to_move}, f)
    print(f"Label mapping saved to {filepath}")

def build_model(input_size, hidden_sizes, output_size):
    """
    Initializes the neural network model.

    Parameters:
    - input_size (int): Number of input features.
    - hidden_sizes (List[int]): Sizes of hidden layers.
    - output_size (int): Number of output classes.

    Returns:
    - ChessMovePredictor: Initialized PyTorch model.
    """
    model = ChessMovePredictor(input_size, hidden_sizes, output_size)
    return model

def main():
    pgn_directory = 'data/'
    model_save_path = 'models/best_move_model.pth'
    label_mapping_path = 'models/labels_mapping.json'

    os.makedirs('models', exist_ok=True)

    # Step 1: Parse PGN files
    print("Parsing PGN files...")
    games = parse_pgn_files(pgn_directory)
    print(f"Total games parsed: {len(games)}")

    # Step 2: Extract moves and board states
    print("Extracting moves from games...")
    data = extract_moves(games, max_moves_per_game=100)
    print(f"Total moves extracted: {len(data)}")

    # Step 3: Prepare dataset
    print("Preparing dataset...")
    X, y_encoded, label_encoder = prepare_dataset(data)
    print(f"Features shape: {X.shape}")
    print(f"Labels shape: {y_encoded.shape}")

    # Step 4: Save label mappings
    print("Saving label mappings...")
    save_label_mapping(label_encoder, label_mapping_path)

    # Step 5: Split data into training and validation sets
    print("Splitting data into training and validation sets...")
    X_train, X_val, y_train, y_val = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, shuffle=True
    )
    print(f"Training set size: {X_train.shape[0]}")
    print(f"Validation set size: {X_val.shape[0]}")

    # Step 6: Build the model
    print("Building the model...")
    input_size = X_train.shape[1]
    hidden_sizes = [1024, 512, 256]
    num_classes = len(label_encoder.classes_)
    model = build_model(input_size, hidden_sizes, num_classes)
    print(model)

    # Step 7: Create Datasets and DataLoaders
    print("Creating datasets and dataloaders...")
    train_dataset = ChessDataset(X_train, y_train)
    val_dataset = ChessDataset(X_val, y_val)

    batch_size = 256
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=2)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=2)

    # Step 8: Define Loss and Optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # Step 9: Training Loop
    num_epochs = 20
    best_val_accuracy = 0.0

    print("Starting training...")
    for epoch in range(num_epochs):
        model.train()
        running_loss = 0.0
        for batch_X, batch_y in tqdm(train_loader, desc=f"Epoch {epoch+1}/{num_epochs} - Training"):
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            running_loss += loss.item()

        avg_train_loss = running_loss / len(train_loader)
        print(f"Epoch [{epoch+1}/{num_epochs}], Training Loss: {avg_train_loss:.4f}")

        model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for batch_X, batch_y in tqdm(val_loader, desc=f"Epoch {epoch+1}/{num_epochs} - Validation"):
                outputs = model(batch_X)
                _, predicted = torch.max(outputs.data, 1)
                total += batch_y.size(0)
                correct += (predicted == batch_y).sum().item()

        val_accuracy = 100 * correct / total
        print(f"Epoch [{epoch+1}/{num_epochs}], Validation Accuracy: {val_accuracy:.2f}%")

        if val_accuracy > best_val_accuracy:
            best_val_accuracy = val_accuracy
            torch.save(model.state_dict(), model_save_path)
            print(f"Model saved with Validation Accuracy: {best_val_accuracy:.2f}%")

    print("Training completed.")

if __name__ == "__main__":
    main()
