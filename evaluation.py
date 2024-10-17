from constants import PIECE_VALUES, POSITIONAL_VALUES, FILE_MASKS, RANK_MASKS

def evaluate(board):
    score = 0
    material_score = 0
    positional_score = 0
    mobility_score = 0
    king_safety_score = 0
    pawn_structure_score = 0
    center_control_score = 0
    piece_coordination_score = 0
    passed_pawn_score = 0
    bishop_pair_score = 0
    rook_on_open_file_score = 0
    queen_mobility_score = 0
    knight_outpost_score = 0

    piece_counts = {'B': 0, 'b': 0}

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

            if piece.upper() == 'B':
                piece_counts[piece] += 1

            if piece.upper() == 'R':
                file = square % 8
                if is_file_open(board, file):
                    if piece.isupper():
                        rook_on_open_file_score += 20
                    else:
                        rook_on_open_file_score -= 20

            if piece.upper() == 'Q':
                mobility = len(board.generate_piece_moves(piece, square))
                if piece.isupper():
                    queen_mobility_score += mobility
                else:
                    queen_mobility_score -= mobility

            if piece.upper() == 'N':
                if is_knight_outpost(board, square, piece.isupper()):
                    if piece.isupper():
                        knight_outpost_score += 30
                    else:
                        knight_outpost_score -= 30

            bitboard &= bitboard - 1

    if piece_counts['B'] >= 2:
        bishop_pair_score += 50
    if piece_counts['b'] >= 2:
        bishop_pair_score -= 50

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

    passed_pawn_score = evaluate_passed_pawns(board)

    score = (material_score +
             positional_score +
             10 * mobility_score +
             king_safety_score +
             pawn_structure_score +
             center_control_score +
             piece_coordination_score +
             passed_pawn_score +
             bishop_pair_score +
             rook_on_open_file_score +
             queen_mobility_score +
             knight_outpost_score)

    if not board.white_to_move:
        score = -score

    return score

def evaluate_king_safety(board):
    score = 0
    own_king_square = board.find_king_square(board.white_to_move)
    if own_king_square is None:
        return -100000 if board.white_to_move else 100000

    enemy_pieces = 'pnbrqk' if board.white_to_move else 'PNBRQK'
    attackers = 0
    attack_weight = 0

    for piece in enemy_pieces:
        bitboard = board.bitboards.get(piece, 0)
        while bitboard:
            from_square = (bitboard & -bitboard).bit_length() - 1
            attacks = board.generate_piece_moves(piece, from_square, attacks_only=True)
            for move in attacks:
                if is_near_king(move.to_square, own_king_square):
                    attackers += 1
                    attack_weight += get_piece_attack_weight(piece)
                    break
            bitboard &= bitboard - 1

    shield_penalty = evaluate_king_pawn_shield(board, own_king_square, board.white_to_move)

    score -= attackers * attack_weight * 10
    score -= shield_penalty

    return score

def is_near_king(square, king_square):
    rank_diff = abs((square // 8) - (king_square // 8))
    file_diff = abs((square % 8) - (king_square % 8))
    return rank_diff <= 1 and file_diff <= 1

def get_piece_attack_weight(piece):
    if piece.upper() == 'P':
        return 1
    if piece.upper() == 'N' or piece.upper() == 'B':
        return 3
    if piece.upper() == 'R':
        return 5
    if piece.upper() == 'Q':
        return 9
    return 0

def evaluate_king_pawn_shield(board, king_square, is_white):
    score = 0
    rank = king_square // 8
    file = king_square % 8
    pawn_piece = 'P' if is_white else 'p'
    direction = 1 if is_white else -1
    shield_rank = rank + direction

    if 0 <= shield_rank < 8:
        for df in [-1, 0, 1]:
            f = file + df
            if 0 <= f < 8:
                sq = shield_rank * 8 + f
                if not (board.bitboards.get(pawn_piece, 0) & (1 << sq)):
                    score += 15
    return score

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
    pawn_ranks = [[] for _ in range(8)]

    pawns_copy = pawns
    while pawns_copy:
        square = (pawns_copy & -pawns_copy).bit_length() - 1
        file = square % 8
        rank = square // 8
        pawn_files[file] += 1
        pawn_ranks[file].append(rank)
        pawns_copy &= pawns_copy - 1

    for file_count in pawn_files:
        if file_count > 1:
            score -= (file_count - 1) * 30

    for i in range(8):
        if pawn_files[i] > 0:
            is_isolated = True
            if i > 0 and pawn_files[i - 1] > 0:
                is_isolated = False
            if i < 7 and pawn_files[i + 1] > 0:
                is_isolated = False
            if is_isolated:
                score -= pawn_files[i] * 25

    for i in range(8):
        if pawn_files[i] > 0:
            for rank in pawn_ranks[i]:
                if is_backward_pawn(board, i, rank, is_white):
                    score -= 20
                if is_doubled_pawn(pawn_ranks[i], rank, is_white):
                    score -= 20

    return score

def is_backward_pawn(board, file, rank, is_white):
    direction = 1 if is_white else -1
    next_rank = rank + direction
    if 0 <= next_rank < 8:
        for df in [-1, 1]:
            f = file + df
            if 0 <= f < 8:
                sq = next_rank * 8 + f
                pawn_piece = 'P' if is_white else 'p'
                if board.bitboards.get(pawn_piece, 0) & (1 << sq):
                    return False
    return True

def is_doubled_pawn(pawn_ranks_in_file, rank, is_white):
    count = pawn_ranks_in_file.count(rank)
    return count > 1

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
            attacks = board.generate_piece_moves(piece, square, attacks_only=True)
            for move in attacks:
                if move.to_square in central_squares:
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
                    score += 10
            bitboard &= bitboard - 1
    return score

def evaluate_passed_pawns(board):
    score = 0
    white_pawns = board.bitboards.get('P', 0)
    black_pawns = board.bitboards.get('p', 0)

    score += evaluate_passed_pawns_for_color(board, white_pawns, black_pawns, is_white=True)
    score -= evaluate_passed_pawns_for_color(board, black_pawns, white_pawns, is_white=False)

    return score

def evaluate_passed_pawns_for_color(board, own_pawns, enemy_pawns, is_white):
    score = 0
    direction = 1 if is_white else -1
    own_pawns_copy = own_pawns
    while own_pawns_copy:
        square = (own_pawns_copy & -own_pawns_copy).bit_length() - 1
        file = square % 8
        rank = square // 8
        if is_pawn_passed(board, square, enemy_pawns, is_white):
            distance_to_promotion = 7 - rank if is_white else rank
            score += (50 + (distance_to_promotion * 10))
        own_pawns_copy &= own_pawns_copy - 1
    return score

def is_pawn_passed(board, square, enemy_pawns, is_white):
    file = square % 8
    rank = square // 8
    direction = 1 if is_white else -1
    for r in range(rank + direction, 8 if is_white else -1, direction):
        for df in [-1, 0, 1]:
            f = file + df
            if 0 <= f < 8:
                sq = r * 8 + f
                if enemy_pawns & (1 << sq):
                    return False
    return True

def is_file_open(board, file):
    for rank in range(8):
        square = rank * 8 + file
        if board.bitboards.get('P', 0) & (1 << square):
            return False
        if board.bitboards.get('p', 0) & (1 << square):
            return False
    return True

def is_knight_outpost(board, square, is_white):
    file = square % 8
    rank = square // 8
    pawn_piece = 'P' if is_white else 'p'
    direction = -1 if is_white else 1
    for df in [-1, 1]:
        f = file + df
        r = rank + direction
        if 0 <= f < 8 and 0 <= r < 8:
            sq = r * 8 + f
            if board.bitboards.get(pawn_piece, 0) & (1 << sq):
                return True
    return False
