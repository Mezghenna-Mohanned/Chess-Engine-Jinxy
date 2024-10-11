from collections import deque

columns = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
rows = [8, 7, 6, 5, 4, 3, 2, 1]

chessboard = [[f"{col}{row}" for col in columns] for row in rows]


for row in chessboard:
    print(row)


def is_valid_position(position):
    if len(position) == 2:
        col, row = position[0], position[1]
        return col in columns and row in '12345678'
    return False


king_position = input("Enter the position of the King (e.g., 'e4'): ").lower()
while not is_valid_position(king_position):
    king_position = input("Invalid position! Enter the position of the King (e.g., 'e4'): ").lower()

knight_position = input("Enter the position of the Knight (e.g., 'g2'): ").lower()
while not is_valid_position(knight_position):
    knight_position = input("Invalid position! Enter the position of the Knight (e.g., 'g2'): ").lower()

print(f"King's position: {king_position}")
print(f"Knight's position: {knight_position}")


knight_moves = [
    (2, 1),   # (x + 2, y + 1)
    (2, -1),  # (x + 2, y - 1)
    (-2, 1),  # (x - 2, y + 1)
    (-2, -1), # (x - 2, y - 1)
    (1, 2),   # (x + 1, y + 2)
    (1, -2),  # (x + 1, y - 2)
    (-1, 2),  # (x - 1, y + 2)
    (-1, -2)  # (x - 1, y - 2)
]


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

        print(f"Visiting: {current_position}, Path so far: {path}")

        if current_position == king_position:
            print(f"Reached the king at: {current_position}")
            return path

        visited.add(current_position)
        print(f"Visited positions: {visited}")

        for move in get_valid_knight_moves(current_position):
            if move not in visited:
                print(f"Adding move: {move} to the queue")
                queue.append((move, path + [move]))

        print(f"Queue state: {list(queue)}")

    return None
shortest_path = bfs_knight_to_king(knight_position, king_position)

if shortest_path:
    print(f"Shortest path for the knight to reach the king: {shortest_path}")
else:
    print("No path found for the knight to reach the king.")
