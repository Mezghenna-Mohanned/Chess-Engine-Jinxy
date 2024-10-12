import random
from collections import deque

columns = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
rows = [8, 7, 6, 5, 4, 3, 2, 1]
knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
king_moves = [(1, 1), (1, -1), (-1, 1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)]

def is_valid_position(position):
    if len(position) == 2:
        col, row = position[0], position[1]
        return col in columns and row in '12345678'
    return False

def random_position():
    col = random.choice(columns)
    row = random.choice('12345678')
    return f"{col}{row}"

def get_valid_knight_moves(knight_position):
    valid_moves = []
    col_index = columns.index(knight_position[0])
    row_index = int(knight_position[1]) - 1

    for move in knight_moves:
        new_col_index = col_index + move[0]
        new_row_index = row_index + move[1]

        if 0 <= new_col_index < 8 and 0 <= new_row_index < 8:
            new_position = f"{columns[new_col_index]}{new_row_index + 1}"
            valid_moves.append(new_position)

    return valid_moves

def bfs_knight_to_king(knight_position, king_position):
    queue = deque([(knight_position, [knight_position])])
    visited = set()

    while queue:
        current_position, path = queue.popleft()

        if current_position == king_position:
            return path

        visited.add(current_position)

        for move in get_valid_knight_moves(current_position):
            if move not in visited:
                queue.append((move, path + [move]))

    return None

def is_valid_king_move(current_king_position, new_king_position):
    col_diff = columns.index(new_king_position[0]) - columns.index(current_king_position[0])
    row_diff = int(new_king_position[1]) - int(current_king_position[1])

    return (col_diff, row_diff) in king_moves

def get_valid_king_moves(king_position, knight_position):
    valid_moves = []
    col_index = columns.index(king_position[0])
    row_index = int(king_position[1]) - 1

    for move in king_moves:
        new_col_index = col_index + move[0]
        new_row_index = row_index + move[1]

        if 0 <= new_col_index < 8 and 0 <= new_row_index < 8:
            new_position = f"{columns[new_col_index]}{new_row_index + 1}"
            if new_position not in get_valid_knight_moves(knight_position):
                valid_moves.append(new_position)

    return valid_moves

def knight_turn(knight_position, king_position):
    path = bfs_knight_to_king(knight_position, king_position)
    if path and len(path) > 1:
        return path[1]
    return knight_position

def king_turn(knight_position, current_king_position):
    valid_moves = get_valid_king_moves(current_king_position, knight_position)
    new_king_position = input(f"Your turn! Enter new King position (e.g., 'e4') avoiding knight at {knight_position}: ").lower()

    while new_king_position not in valid_moves:
        new_king_position = input(f"Invalid move! That square is under the knight's threat or not valid. Pick another position: ").lower()

    return new_king_position

def is_king_in_check(knight_position, king_position):
    return king_position in get_valid_knight_moves(knight_position)

def can_king_capture_knight(knight_position, king_position):
    return knight_position in get_valid_king_moves(king_position, knight_position)

def game_loop():
    knight_position = random_position()
    print(f"Knight starts at {knight_position}")
    king_position = input("Enter the initial position of the King (e.g., 'e4'): ").lower()

    while not is_valid_position(king_position):
        king_position = input("Invalid position! Enter a valid initial position for the King: ").lower()

    print(f"Game start! Knight starts at {knight_position}, King starts at {king_position}")

    while knight_position != king_position:
        knight_position = knight_turn(knight_position, king_position)

        if is_king_in_check(knight_position, king_position):
            print(f"Check! The knight is threatening the King at {king_position}!")

        if can_king_capture_knight(knight_position, king_position):
            print(f"King captured the Knight at {knight_position}! You win!")
            break

        king_position = king_turn(knight_position, king_position)

    if knight_position == king_position:
        print("The knight captured the king! Game over.")

if __name__ == "__main__":
    game_loop()
