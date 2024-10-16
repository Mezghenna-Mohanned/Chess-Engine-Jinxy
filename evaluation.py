from constants import PIECE_VALUES, POSITIONAL_VALUES

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
                positional_value = POSITIONAL_VALUES[piece.upper()][square]
                if piece.islower():
                    positional_value = -positional_value
            piece_material_value = piece_value
            if piece.islower():
                piece_material_value = -piece_material_value
            material_score += piece_material_value
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

    return score

def evaluate_king_safety(board):
    score = 0
    own_king_square = board.find_king_square(board.white_to_move)
    if own_king_square is None:
        return -10000 if board.white_to_move else 10000
    
    king_neighbors = []
    king_row = own_king_square // 8
    king_col = own_king_square % 8
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            r = king_row + dr
            c = king_col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                neighbor_square = r * 8 + c
                king_neighbors.append(neighbor_square)

    num_attacked_squares = 0
    for square in king_neighbors:
        if board.is_square_attacked(square, not board.white_to_move):
            num_attacked_squares += 1
    score -= num_attacked_squares * 0.5

    pawn_shield_squares = []
    if board.white_to_move:
        pawn_shield_row = king_row + 1
        pawn_piece = 'P'
    else:
        pawn_shield_row = king_row - 1
        pawn_piece = 'p'
    for dc in [-1, 0, 1]:
        r = pawn_shield_row
        c = king_col + dc
        if 0 <= r < 8 and 0 <= c < 8:
            shield_square = r * 8 + c
            pawn_shield_squares.append(shield_square)

    missing_pawns = 0
    for square in pawn_shield_squares:
        piece = board.get_piece_at_square(square)
        if piece != pawn_piece:
            missing_pawns += 1
    score -= missing_pawns * 0.3

    if board.white_to_move:
        if not board.castling_rights['K'] and not board.castling_rights['Q']:
            if own_king_square in range(4, 8):
                score -= 0.5
    else:
        if not board.castling_rights['k'] and not board.castling_rights['q']:
            if own_king_square in range(60, 64):
                score -= 0.5

    return score

def evaluate_pawn_structure(board):
    score = 0
    white_pawns = board.bitboards.get('P', 0)
    black_pawns = board.bitboards.get('p', 0)

    white_pawn_files = [0] * 8
    black_pawn_files = [0] * 8

    wpawns = white_pawns
    while wpawns:
        square = (wpawns & -wpawns).bit_length() - 1
        file = square % 8
        white_pawn_files[file] += 1
        wpawns &= wpawns - 1

    bpawns = black_pawns
    while bpawns:
        square = (bpawns & -bpawns).bit_length() - 1
        file = square % 8
        black_pawn_files[file] += 1
        bpawns &= bpawns - 1

    for i in range(8):
        if white_pawn_files[i] > 1:
            score -= (white_pawn_files[i] - 1) * 0.5
        if black_pawn_files[i] > 1:
            score += (black_pawn_files[i] - 1) * 0.5

    for i in range(8):
        if white_pawn_files[i] > 0:
            if (i == 0 or white_pawn_files[i - 1] == 0) and (i == 7 or white_pawn_files[i + 1] == 0):
                score -= 0.5 * white_pawn_files[i]
        if black_pawn_files[i] > 0:
            if (i == 0 or black_pawn_files[i - 1] == 0) and (i == 7 or black_pawn_files[i + 1] == 0):
                score += 0.5 * black_pawn_files[i]

    for i in range(8):
        if white_pawn_files[i] > 0:
            is_passed = True
            for j in [i - 1, i, i + 1]:
                if 0 <= j < 8:
                    if black_pawn_files[j] > 0:
                        is_passed = False
                        break
            if is_passed:
                score += 0.5 * white_pawn_files[i]

        if black_pawn_files[i] > 0:
            is_passed = True
            for j in [i - 1, i, i + 1]:
                if 0 <= j < 8:
                    if white_pawn_files[j] > 0:
                        is_passed = False
                        break
            if is_passed:
                score -= 0.5 * black_pawn_files[i]

    return score

def evaluate_center_control(board):
    score = 0
    central_squares = [27, 28, 35, 36]  # d4, e4, d5, e5

    for piece, bitboard in board.bitboards.items():
        while bitboard:
            square = (bitboard & -bitboard).bit_length() - 1
            controls_center = False
            if square in central_squares:
                controls_center = True
            else:
                moves = board.generate_piece_moves(piece, square)
                for move in moves:
                    if move.to_square in central_squares:
                        controls_center = True
                        break
            if controls_center:
                if piece.isupper():
                    score += 0.1
                else:
                    score -= 0.1
            bitboard &= bitboard - 1

    return score

def evaluate_piece_coordination(board):
    score = 0
    own_pieces = 'PNBRQK' if board.white_to_move else 'pnbrqk'

    for piece in own_pieces:
        bitboard = board.bitboards.get(piece, 0)
        while bitboard:
            square = (bitboard & -bitboard).bit_length() - 1
            if is_square_defended_by(board, square, board.white_to_move):
                score += 0.1 if board.white_to_move else -0.1
            bitboard &= bitboard - 1

    return score

def is_square_defended_by(board, square, own_side):
    defended = False
    own_pieces = 'PNBRQK' if own_side else 'pnbrqk'
    for piece in own_pieces:
        bitboard = board.bitboards.get(piece, 0)
        while bitboard:
            from_square = (bitboard & -bitboard).bit_length() - 1
            moves = board.generate_piece_moves(piece, from_square, attacks_only=True)
            for move in moves:
                if move.to_square == square:
                    return True
            bitboard &= bitboard - 1
    return False
