from constants import PIECE_VALUES, POSITIONAL_VALUES, FILE_MASKS

def evaluate(board):
    score = 0
    material_score = 0
    positional_score = 0
    mobility_score = 0
    king_safety_score = 0
    pawn_structure_score = 0
    center_control_score = 0
    piece_coordination_score = 0

    for piece, bitboard in board.bitboards.items():
        piece_value = PIECE_VALUES[piece]
        while bitboard:
            square = (bitboard & -bitboard).bit_length() - 1
            positional_value = 0
            if piece.upper() in POSITIONAL_VALUES:
                index = square if piece.isupper() else 63 - square
                positional_value = POSITIONAL_VALUES[piece.upper()][index]
                if piece.islower():
                    positional_value = -positional_value
            material_score += piece_value
            positional_score += positional_value
            bitboard &= bitboard - 1


    own_moves = board.generate_legal_moves()
    own_mobility = len(own_moves)
    board.white_to_move = not board.white_to_move
    opponent_moves = board.generate_legal_moves()
    opponent_mobility = len(opponent_moves)
    board.white_to_move = not board.white_to_move
    mobility_score = own_mobility - opponent_mobility


    king_safety_score = evaluate_king_safety(board)

    pawn_structure_score = evaluate_pawn_structure(board)

    center_control_score = evaluate_center_control(board)

    piece_coordination_score = evaluate_piece_coordination(board)

    score = (material_score +
             positional_score +
             0.1 * mobility_score +
             king_safety_score +
             pawn_structure_score +
             center_control_score +
             piece_coordination_score)

    if not board.white_to_move:
        score = -score

    return score

def evaluate_king_safety(board):
    score = 0
    own_king_square = board.find_king_square(board.white_to_move)
    if own_king_square is None:
        return -10000 if board.white_to_move else 10000
    danger_squares = get_adjacent_squares(own_king_square)
    enemy_pieces = 'pnbrqk' if board.white_to_move else 'PNBRQK'
    num_attackers = 0

    for piece in enemy_pieces:
        bitboard = board.bitboards.get(piece, 0)
        while bitboard:
            from_square = (bitboard & -bitboard).bit_length() - 1
            attacks = board.generate_piece_moves(piece, from_square, attacks_only=True)
            for move in attacks:
                if move.to_square in danger_squares:
                    num_attackers += 1
                    break
            bitboard &= bitboard - 1

    score -= num_attackers * 50

    return score

def get_adjacent_squares(square):
    adjacent_squares = []
    rank = square // 8
    file = square % 8
    for dr in [-1, 0, 1]:
        for df in [-1, 0, 1]:
            if dr == 0 and df == 0:
                continue
            r = rank + dr
            f = file + df
            if 0 <= r < 8 and 0 <= f < 8:
                adjacent_squares.append(r * 8 + f)
    return adjacent_squares

def evaluate_pawn_structure(board):
    score = 0
    white_pawns = board.bitboards.get('P', 0)
    black_pawns = board.bitboards.get('p', 0)

    score += evaluate_pawn_weaknesses(board, white_pawns, is_white=True)

    score -= evaluate_pawn_weaknesses(board, black_pawns, is_white=False)

    return score

def evaluate_pawn_weaknesses(board, pawns, is_white):
    score = 0
    pawn_files = [0] * 8

    pawns_copy = pawns
    while pawns_copy:
        square = (pawns_copy & -pawns_copy).bit_length() - 1
        file = square % 8
        rank = square // 8
        pawn_files[file] += 1
        pawns_copy &= pawns_copy - 1

    for file_count in pawn_files:
        if file_count > 1:
            score -= (file_count - 1) * 20

    for i in range(8):
        if pawn_files[i] > 0:
            is_isolated = True
            if i > 0 and pawn_files[i - 1] > 0:
                is_isolated = False
            if i < 7 and pawn_files[i + 1] > 0:
                is_isolated = False
            if is_isolated:
                score -= pawn_files[i] * 15
    for i in range(8):
        if pawn_files[i] > 0:
            if is_white:
                opponent_pawns = board.bitboards.get('p', 0)
            else:
                opponent_pawns = board.bitboards.get('P', 0)
            if not has_opponent_pawns_in_front(board, i, opponent_pawns, is_white):
                score += pawn_files[i] * 30

    return score

def has_opponent_pawns_in_front(board, file_index, opponent_pawns, is_white):
    files_to_check = [file_index]
    if file_index > 0:
        files_to_check.append(file_index - 1)
    if file_index < 7:
        files_to_check.append(file_index + 1)

    for file in files_to_check:
        pawns_in_file = opponent_pawns & FILE_MASKS[file]
        while pawns_in_file:
            square = (pawns_in_file & -pawns_in_file).bit_length() - 1
            rank = square // 8
            if is_white and rank > (square // 8):
                return True
            elif not is_white and rank < (square // 8):
                return True
            pawns_in_file &= pawns_in_file - 1
    return False

def evaluate_center_control(board):
    score = 0
    central_squares = [27, 28, 35, 36]
    for piece, bitboard in board.bitboards.items():
        piece_value = 0
        if piece.upper() == 'P':
            piece_value = 10
        elif piece.upper() == 'N' or piece.upper() == 'B':
            piece_value = 30
        elif piece.upper() == 'R':
            piece_value = 50
        elif piece.upper() == 'Q':
            piece_value = 90
        else:
            continue

        while bitboard:
            square = (bitboard & -bitboard).bit_length() - 1
            if square in central_squares:
                if piece.isupper():
                    score += piece_value
                else:
                    score -= piece_value
            bitboard &= bitboard - 1
    return score

def evaluate_piece_coordination(board):
    score = 0
    own_pieces = 'PNBRQK' if board.white_to_move else 'pnbrqk'
    for piece in own_pieces:
        bitboard = board.bitboards.get(piece, 0)
        while bitboard:
            from_square = (bitboard & -bitboard).bit_length() - 1
            attacks = board.generate_piece_moves(piece, from_square, attacks_only=True)
            for move in attacks:
                target_piece = board.get_piece_at_square(move.to_square)
                if target_piece and target_piece in own_pieces:
                    score += 5
            bitboard &= bitboard - 1
    return score
