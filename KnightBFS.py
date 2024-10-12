import random
from collections import deque

columns = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
rows = [8, 7, 6, 5, 4, 3, 2, 1]
chessboard = [[f"{col}{row}" for col in columns] for row in rows]

knight_moves = [
    (2, 1), (2, -1), (-2, 1), (-2, -1),
    (1, 2), (1, -2), (-1, 2), (-1, -2)
]

def is_valid_position(position):
    """Check if the entered position is valid."""
    if len(position) == 2:
        col, row = position[0], position[1]
        return col in columns and row in '12345678'
    return False

def random_position():
    """Get a random valid position on the chessboard."""
    col = random.choice(columns)
    row = random.choice('12345678')
    return f"{col}{row}"

def get_valid_knight_moves(knight_position):
    """Get all valid knight moves from a given position."""
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
    """Use BFS to get the shortest path from the knight to the king."""
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

def knight_turn(knight_position, king_position):
    """Program's turn to move the knight towards the king."""
    print(f"Knight's current position: {knight_position}")
    path = bfs_knight_to_king(knight_position, king_position)
    if path and len(path) > 1:
        new_knight_position = path[1]
        print(f"Knight moves to: {new_knight_position}")
        return new_knight_position
    return knight_position

def king_turn(knight_position, current_king_position):
    """Player's turn to move the king. The king cannot stay in the same position."""
    new_king_position = input(f"Your turn! Enter new King position (e.g., 'e4') avoiding knight at {knight_position}: ").lower()

    while not is_valid_position(new_king_position) or new_king_position == current_king_position or new_king_position == knight_position:
        new_king_position = input("Invalid or blocked position! Enter a valid new position: ").lower()

    return new_king_position

def is_king_in_check(knight_position, king_position):
    """Check if the king is in check (knight can reach king next move)."""
    return king_position in get_valid_knight_moves(knight_position)

def game_loop():
    """Main game loop where knight and king take turns."""
    knight_position = random_position()
    king_position = random_position()

    print(f"Game start! Knight starts at {knight_position}, King starts at {king_position}")

    while knight_position != king_position:

        knight_position = knight_turn(knight_position, king_position)

        if knight_position == king_position:
            print(f"Knight caught the King at {knight_position}! Game over.")
            break

        if is_king_in_check(knight_position, king_position):
            print(f"Check! The knight is threatening the King at {king_position}!")

        king_position = king_turn(knight_position, king_position)

        print(f"King moved to: {king_position}")

    if knight_position == king_position:
        print("The knight captured the king! Game over.")

if __name__ == "__main__":
    game_loop()
