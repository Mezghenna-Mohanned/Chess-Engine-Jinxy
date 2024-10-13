import random
from collections import deque

columns = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
rows = ['8', '7', '6', '5', '4', '3', '2', '1']
knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
rook_directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
king_moves = [(1, 1), (1, -1), (-1, 1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)]

def is_valid_position(position):
    return len(position) == 2 and position[0] in columns and position[1] in rows

def random_position():
    col = random.choice(columns)
    row = random.choice(rows)
    return f"{col}{row}"

def get_valid_knight_moves(knight_position):
    col = knight_position[0]
    row = knight_position[1]
    valid_moves = []
    
    for move in knight_moves:
        new_col_idx = columns.index(col) + move[0]
        new_row_idx = rows.index(row) + move[1]
        
        if 0 <= new_col_idx < 8 and 0 <= new_row_idx < 8:
            new_col = columns[new_col_idx]
            new_row = rows[new_row_idx]
            valid_moves.append(f"{new_col}{new_row}")
    
    return valid_moves

def bfs_knight_to_king(knight_position, king_position):
    queue = deque([(knight_position, [knight_position])])
    visited = set([knight_position])
    
    while queue:
        current_position, path = queue.popleft()
        
        if current_position == king_position:
            return path
        
        for move in get_valid_knight_moves(current_position):
            if move not in visited:
                visited.add(move)
                queue.append((move, path + [move]))
    
    return None

def knight_turn(knight_position, king_position):
    valid_knight_moves = get_valid_knight_moves(knight_position)
    
    if king_position in valid_knight_moves:
        print(f"Knight checks the King from {knight_position}")
        return knight_position

    knight_path = bfs_knight_to_king(knight_position, king_position)
    
    if knight_path and len(knight_path) > 1:
        next_knight_position = knight_path[1]
        print(f"Knight moves from {knight_position} to {next_knight_position}")
        return next_knight_position
    
    return knight_position


def get_valid_rook_moves(rook_position):
    col = rook_position[0]
    row = rook_position[1]
    valid_moves = []
    
    for direction in rook_directions:
        new_col_idx = columns.index(col)
        new_row_idx = rows.index(row)
        
        while True:
            new_col_idx += direction[0]
            new_row_idx += direction[1]
            
            if 0 <= new_col_idx < 8 and 0 <= new_row_idx < 8:
                new_col = columns[new_col_idx]
                new_row = rows[new_row_idx]
                valid_moves.append(f"{new_col}{new_row}")
            else:
                break
    
    return valid_moves


def bfs_rook_to_king(rook_position, king_position):
    queue = deque([(rook_position, [rook_position])])
    visited = set([rook_position])
    
    while queue:
        current_position, path = queue.popleft()
        
        if current_position == king_position:
            return path
        
        for move in get_valid_rook_moves(current_position):
            if move not in visited:
                visited.add(move)
                queue.append((move, path + [move]))
    
    return None


def rook_turn(rook_position, king_position):
    valid_rook_moves = get_valid_rook_moves(rook_position)

    safe_moves = [move for move in valid_rook_moves if move not in get_valid_king_moves(king_position)]
    
    if king_position in valid_rook_moves:
        print(f"Rook checks the King from {rook_position}")
        return rook_position

    if safe_moves:
        next_rook_position = safe_moves[0]
        print(f"Rook moves from {rook_position} to {next_rook_position}")
        return next_rook_position
    
    return rook_position



def get_valid_king_moves(king_position):
    col = king_position[0]
    row = king_position[1]
    valid_moves = []
    
    for move in king_moves:
        new_col_idx = columns.index(col) + move[0]
        new_row_idx = rows.index(row) + move[1]
        
        if 0 <= new_col_idx < 8 and 0 <= new_row_idx < 8:
            new_col = columns[new_col_idx]
            new_row = rows[new_row_idx]
            valid_moves.append(f"{new_col}{new_row}")
    
    return valid_moves


def user_move_king(king_position):
    while True:
        move = input("Enter King's move (e.g., 'e4'): ").lower().strip()
        if is_valid_position(move) and move in get_valid_king_moves(king_position):
            return move
        else:
            print("Invalid move. Please try again.")


def best_move(knight_position, rook_position, king_position):
    knight_check_moves = get_valid_knight_moves(knight_position)
    rook_check_moves = get_valid_rook_moves(rook_position)
    
    if king_position in knight_check_moves:
        return knight_position, rook_position
    elif king_position in rook_check_moves:
        return knight_position, rook_position
    
    knight_path = bfs_knight_to_king(knight_position, king_position)
    rook_path = bfs_rook_to_king(rook_position, king_position)
    
    if knight_path and len(knight_path) > 1 and rook_path and len(rook_path) > 1:
        if len(knight_path) <= len(rook_path):
            knight_position = knight_path[1]
        else:
            rook_position = rook_path[1]
    elif knight_path and len(knight_path) > 1:
        knight_position = knight_path[1]
    elif rook_path and len(rook_path) > 1:
        rook_position = rook_path[1]
    
    return knight_position, rook_position


def is_king_in_check(king_position, knight_position, rook_position):
    if king_position in get_valid_knight_moves(knight_position):
        return "Check by Knight!"
    elif king_position in get_valid_rook_moves(rook_position):
        return "Check by Rook!"
    return None


def is_checkmate(knight_position, rook_position, king_position):
    valid_king_moves = get_valid_king_moves(king_position)
    safe_moves = [move for move in valid_king_moves if move not in get_valid_knight_moves(knight_position) and move not in get_valid_rook_moves(rook_position)]
    return len(safe_moves) == 0 and (king_position in get_valid_knight_moves(knight_position) or king_position in get_valid_rook_moves(rook_position))



def game_loop():
    knight_position = random_position()
    rook_position = random_position()
    print(f"Knight starts at {knight_position}, Rook starts at {rook_position}")
    
    king_position = input("Enter the initial position of the King (e.g., 'e4'): ").lower()

    while not is_valid_position(king_position):
        king_position = input("Invalid position! Enter a valid initial position for the King: ").lower()

    print(f"Game start! Knight starts at {knight_position}, Rook starts at {rook_position}, King starts at {king_position}")
    
    turn = 1
    while not is_checkmate(knight_position, rook_position, king_position):
        print(f"\nTurn {turn}:")
        print(f"Knight: {knight_position}, Rook: {rook_position}, King: {king_position}")
        
        check_status = is_king_in_check(king_position, knight_position, rook_position)
        if check_status:
            print(check_status)
        
        knight_position = knight_turn(knight_position, king_position)

        rook_position = rook_turn(rook_position, king_position)
        print(f"After move: Knight: {knight_position}, Rook: {rook_position}")

        king_position = user_move_king(king_position)
        print(f"King moves to {king_position}")

        if king_position == rook_position:
            print(f"The King has captured the Rook at {rook_position}!")
            rook_position = None
            break

        turn += 1
    
    if is_checkmate(knight_position, rook_position, king_position):
        print("Checkmate! The King cannot move anymore.")

game_loop()
