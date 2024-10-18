import numpy as np
from functools import lru_cache
from constants import PIECE_VALUES, POSITIONAL_VALUES, FILE_MASKS

PIECE_SQUARE_TABLES = {
    'P': np.array([
         0,   0,   0,   0,   0,   0,   0,   0,
         5,  10,  10, -20, -20,  10,  10,   5,
         5,  -5, -10,   0,   0, -10,  -5,   5,
         0,   0,   0,  20,  20,   0,   0,   0,
         5,   5,  10,  25,  25,  10,   5,   5,
        10,  10,  20,  30,  30,  20,  10,  10,
        50,  50,  50,  50,  50,  50,  50,  50,
         0,   0,   0,   0,   0,   0,   0,   0
    ]),
    'N': np.array([
       -50, -40, -30, -30, -30, -30, -40, -50,
       -40, -20,   0,   0,   0,   0, -20, -40,
       -30,   0,  10,  15,  15,  10,   0, -30,
       -30,   5,  15,  20,  20,  15,   5, -30,
       -30,   0,  15,  20,  20,  15,   0, -30,
       -30,   5,  10,  15,  15,  10,   5, -30,
       -40, -20,   0,   5,   5,   0, -20, -40,
       -50, -40, -30, -30, -30, -30, -40, -50
    ]),
    'B': np.array([
       -20, -10, -10, -10, -10, -10, -10, -20,
       -10,   5,   0,   0,   0,   0,   5, -10,
       -10,  10,  10,  10,  10,  10,  10, -10,
       -10,   0,  10,  10,  10,  10,   0, -10,
       -10,   5,   5,  10,  10,   5,   5, -10,
       -10,   0,   5,  10,  10,   5,   0, -10,
       -10,   0,   0,   0,   0,   0,   0, -10,
       -20, -10, -10, -10, -10, -10, -10, -20
    ]),
    'R': np.array([
         0,   0,   0,   5,   5,   0,   0,   0,
        -5,   0,   0,   0,   0,   0,   0,  -5,
        -5,   0,   0,   0,   0,   0,   0,  -5,
        -5,   0,   0,   0,   0,   0,   0,  -5,
        -5,   0,   0,   0,   0,   0,   0,  -5,
        -5,   0,   0,   0,   0,   0,   0,  -5,
         5,  10,  10,  10,  10,  10,  10,   5,
         0,   0,   0,   0,   0,   0,   0,   0
    ]),
    'Q': np.array([
       -20, -10, -10,  -5,  -5, -10, -10, -20,
       -10,   0,   0,   0,   0,   0,   0, -10,
       -10,   0,   5,   5,   5,   5,   0, -10,
        -5,   0,   5,   5,   5,   5,   0,  -5,
         0,   0,   5,   5,   5,   5,   0,  -5,
       -10,   5,   5,   5,   5,   5,   0, -10,
       -10,   0,   5,   0,   0,   0,   0, -10,
       -20, -10, -10,  -5,  -5, -10, -10, -20
    ]),
    'K': np.array([
       -30, -40, -40, -50, -50, -40, -40, -30,
       -30, -40, -40, -50, -50, -40, -40, -30,
       -30, -40, -40, -50, -50, -40, -40, -30,
       -30, -40, -40, -50, -50, -40, -40, -30,
       -20, -30, -30, -40, -40, -30, -30, -20,
       -10, -20, -20, -20, -20, -20, -20, -10,
        20,  20,   0,   0,   0,   0,  20,  20,
        20,  30,  10,   0,   0,  10,  30,  20
    ]),
}

@lru_cache(maxsize=None)
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
    knight_outpost_score = 0
    threats_score = 0
    space_score = 0
    development_score = 0
    opponent_weaknesses_score = 0
    exchange_score = 0

    phase = get_game_phase(board)
    piece_counts = {'B': 0, 'b': 0, 'N': 0, 'n': 0}
    own_pieces = 'PNBRQK' if board.white_to_move else 'pnbrqk'
    enemy_pieces = 'pnbrqk' if board.white_to_move else 'PNBRQK'

    for piece in own_pieces + enemy_pieces:
        bitboard = board.bitboards.get(piece, 0)
        piece_value = PIECE_VALUES.get(piece.upper(), 0)
        if bitboard:
            squares = [i for i in range(64) if bitboard & (1 << i)]
            material_score += piece_value * len(squares)
            if piece.upper() in PIECE_SQUARE_TABLES:
                table = PIECE_SQUARE_TABLES[piece.upper()]
                squares_np = np.array(squares)
                if piece.isupper():
                    positional_values = table[squares_np]
                else:
                    positional_values = -table[63 - squares_np]
                positional_score += np.sum(positional_values)
            if piece.upper() in ('N', 'B'):
                piece_counts[piece] += len(squares)
            if piece.upper() == 'Q':
                queen_mobility_score = evaluate_mobility(board, piece, squares)
                mobility_score += queen_mobility_score
            else:
                mobility_score += evaluate_mobility(board, piece, squares)
            space_score += evaluate_space(piece, squares)
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
    mobility_score += own_mobility - opponent_mobility
    king_safety_score = evaluate_king_safety(board)
    pawn_structure_score = evaluate_pawn_structure(board)
    center_control_score = evaluate_center_control(board)
    piece_coordination_score = evaluate_piece_coordination(board)
    passed_pawn_score = evaluate_passed_pawns(board)
    threats_score = evaluate_threats(board, own_moves)
    opponent_weaknesses_score = evaluate_opponent_weaknesses(board)
    development_score = evaluate_development(board)
    exchange_score = evaluate_exchanges(board)

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
             knight_outpost_score +
             threats_score +
             space_score +
             development_score +
             opponent_weaknesses_score +
             exchange_score)

    if phase == 'endgame':
        endgame_score = evaluate_endgame(board)
        score += endgame_score

    if not board.white_to_move:
        score = -score

    return score

def get_game_phase(board):
    total_material = 0
    for piece, bitboard in board.bitboards.items():
        if piece.upper() != 'K':
            piece_value = abs(PIECE_VALUES.get(piece.upper(), 0))
            total_material += piece_value * bin(bitboard).count('1')
    if total_material > 32000:
        return 'opening'
    elif total_material > 20000:
        return 'middlegame'
    else:
        return 'endgame'

def evaluate_mobility(board, piece, squares):
    mobility = 0
    for square in squares:
        moves = board.generate_piece_moves(piece, square)
        mobility += len(moves)
    return mobility

def evaluate_space(piece, squares):
    score = 0
    ranks = np.array(squares) // 8
    if piece.isupper():
        score += np.sum(ranks >= 4) * 5
    else:
        score += np.sum(ranks <= 3) * 5
    return score

def evaluate_king_safety(board):
    score = 0
    own_king_square = board.find_king_square(board.white_to_move)
    if own_king_square is None:
        return -100000 if board.white_to_move else 100000
    enemy_moves = board.generate_legal_moves()
    attack_zones = get_king_attack_zones(own_king_square)
    attack_score = sum(get_piece_attack_weight(move.piece) for move in enemy_moves if move.to_square in attack_zones)
    shield_penalty = evaluate_king_pawn_shield(board, own_king_square, board.white_to_move)
    open_file_penalty = evaluate_open_files_to_king(board, own_king_square, board.white_to_move)
    score -= attack_score * 10
    score -= shield_penalty
    score -= open_file_penalty
    return score

def get_king_attack_zones(king_square):
    adjacent = get_adjacent_squares(king_square)
    extended_zone = set(adjacent)
    for square in adjacent:
        extended_zone.update(get_adjacent_squares(square))
    return extended_zone

def evaluate_king_pawn_shield(board, king_square, is_white):
    score = 0
    rank = king_square // 8
    file = king_square % 8
    pawn_piece = 'P' if is_white else 'p'
    direction = 1 if is_white else -1
    for i in range(1, 3):
        shield_rank = rank + i * direction
        if 0 <= shield_rank < 8:
            for df in [-1, 0, 1]:
                f = file + df
                if 0 <= f < 8:
                    sq = shield_rank * 8 + f
                    if not (board.bitboards.get(pawn_piece, 0) & (1 << sq)):
                        score += 10
    return score

def evaluate_open_files_to_king(board, king_square, is_white):
    score = 0
    file = king_square % 8
    enemy_rooks_queens = board.bitboards.get('r' if is_white else 'R', 0) | board.bitboards.get('q' if is_white else 'Q', 0)
    if is_file_open(board, file):
        enemy_pieces = [i for i in range(64) if enemy_rooks_queens & (1 << i)]
        if any(sq % 8 == file for sq in enemy_pieces):
            score += 30
    return score

def get_piece_attack_weight(piece):
    if piece.upper() == 'P':
        return 1
    if piece.upper() in ('N', 'B'):
        return 3
    if piece.upper() == 'R':
        return 5
    if piece.upper() == 'Q':
        return 9
    return 0

def evaluate_pawn_structure(board):
    score = 0
    white_pawns = board.bitboards.get('P', 0)
    black_pawns = board.bitboards.get('p', 0)
    score += evaluate_pawn_weaknesses(board, white_pawns)
    score -= evaluate_pawn_weaknesses(board, black_pawns)
    score += evaluate_pawn_islands(white_pawns)
    score -= evaluate_pawn_islands(black_pawns)
    return score

def evaluate_pawn_weaknesses(board, pawns):
    score = 0
    files = [i % 8 for i in range(64) if pawns & (1 << i)]
    unique_files = set(files)
    counts = {f: files.count(f) for f in unique_files}
    for file, count in counts.items():
        doubled_pawns = count - 1
        score -= doubled_pawns * 30
        is_isolated = True
        if file > 0 and any(f == file - 1 for f in unique_files):
            is_isolated = False
        if file < 7 and any(f == file + 1 for f in unique_files):
            is_isolated = False
        if is_isolated:
            score -= 25
    return score

def evaluate_pawn_islands(pawns):
    files = [i % 8 for i in range(64) if pawns & (1 << i)]
    if not files:
        return 0
    pawn_islands = 1
    files.sort()
    for i in range(1, len(files)):
        if files[i] != files[i - 1]:
            pawn_islands += 1
    return -pawn_islands * 15

def evaluate_center_control(board):
    score = 0
    central_squares = [18, 19, 20, 21, 26, 27, 28, 29, 34, 35, 36, 37, 42, 43, 44, 45]
    own_pieces = 'PNBRQK' if board.white_to_move else 'pnbrqk'
    piece_values = {'P': 10, 'N': 30, 'B': 30, 'R': 50, 'Q': 90}
    for piece in own_pieces:
        bitboard = board.bitboards.get(piece, 0)
        if bitboard:
            squares = [i for i in range(64) if bitboard & (1 << i)]
            for square in squares:
                attacks = board.generate_piece_moves(piece, square, attacks_only=True)
                for move in attacks:
                    if move.to_square in central_squares:
                        score += piece_values.get(piece.upper(), 0)
    return score

def evaluate_piece_coordination(board):
    score = 0
    own_pieces = 'PNBRQK' if board.white_to_move else 'pnbrqk'
    for piece in own_pieces:
        bitboard = board.bitboards.get(piece, 0)
        if bitboard:
            squares = [i for i in range(64) if bitboard & (1 << i)]
            for from_square in squares:
                attacks = board.generate_piece_moves(piece, from_square, attacks_only=True)
                for move in attacks:
                    target_piece = board.get_piece_at_square(move.to_square)
                    if target_piece and target_piece in own_pieces:
                        score += 10
    return score

def evaluate_passed_pawns(board):
    score = 0
    white_pawns = board.bitboards.get('P', 0)
    black_pawns = board.bitboards.get('p', 0)
    score += evaluate_passed_pawns_for_color(board, white_pawns, black_pawns, True)
    score -= evaluate_passed_pawns_for_color(board, black_pawns, white_pawns, False)
    return score

def evaluate_passed_pawns_for_color(board, own_pawns, enemy_pawns, is_white):
    score = 0
    own_pawn_squares = [i for i in range(64) if own_pawns & (1 << i)]
    for square in own_pawn_squares:
        if is_pawn_passed(square, enemy_pawns, is_white):
            rank = square // 8
            distance = 7 - rank if is_white else rank
            base_score = 50 + distance * 10
            if is_protected_passed_pawn(board, square, is_white):
                base_score += 30
            score += base_score
    return score

def is_pawn_passed(square, enemy_pawns, is_white):
    file = square % 8
    rank = square // 8
    direction = 1 if is_white else -1
    start_rank = rank + direction
    end_rank = 8 if is_white else -1
    for r in range(start_rank, end_rank, direction):
        for df in [-1, 0, 1]:
            f = file + df
            if 0 <= f < 8:
                sq = r * 8 + f
                if enemy_pawns & (1 << sq):
                    return False
    return True

def is_protected_passed_pawn(board, square, is_white):
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

def evaluate_threats(board, own_moves):
    score = 0
    for move in own_moves:
        if board.is_capture_move(move):
            captured_value = abs(PIECE_VALUES.get(move.captured_piece.upper(), 0))
            attacker_value = abs(PIECE_VALUES.get(move.piece.upper(), 0))
            trade_gain = captured_value - attacker_value
            score += trade_gain
        elif is_threatening_move(board, move):
            score += 15
    return score

def is_threatening_move(board, move):
    target_piece = board.get_piece_at_square(move.to_square)
    if target_piece and target_piece.islower() != move.piece.islower():
        return True
    return False

def evaluate_opponent_weaknesses(board):
    score = 0
    enemy_pieces = 'pnbrqk' if board.white_to_move else 'PNBRQK'
    for piece in enemy_pieces:
        bitboard = board.bitboards.get(piece, 0)
        if bitboard:
            squares = [i for i in range(64) if bitboard & (1 << i)]
            for square in squares:
                if is_piece_undefended(board, square):
                    score += 20
    return score

def is_piece_undefended(board, square):
    own_pieces = 'PNBRQK' if board.white_to_move else 'pnbrqk'
    for piece in own_pieces:
        bitboard = board.bitboards.get(piece, 0)
        if bitboard:
            from_squares = [i for i in range(64) if bitboard & (1 << i)]
            for from_square in from_squares:
                attacks = board.generate_piece_moves(piece, from_square, attacks_only=True)
                if any(move.to_square == square for move in attacks):
                    return False
    return True

def evaluate_development(board):
    score = 0
    own_pieces = 'PNBRQ' if board.white_to_move else 'pnbrq'
    starting_rank = 0 if board.white_to_move else 7
    for piece in own_pieces:
        bitboard = board.bitboards.get(piece, 0)
        if bitboard:
            squares = [i for i in range(64) if bitboard & (1 << i)]
            for square in squares:
                rank = square // 8
                if rank == starting_rank:
                    score -= 10
    return score

def evaluate_endgame(board):
    score = 0
    own_king_square = board.find_king_square(board.white_to_move)
    enemy_king_square = board.find_king_square(not board.white_to_move)
    own_king_distance = manhattan_distance(own_king_square, enemy_king_square)
    score += (14 - own_king_distance) * 10
    return score

def manhattan_distance(sq1, sq2):
    if sq1 is None or sq2 is None:
        return 0
    rank1, file1 = divmod(sq1, 8)
    rank2, file2 = divmod(sq2, 8)
    return abs(rank1 - rank2) + abs(file1 - file2)

def evaluate_exchanges(board):
    score = 0
    own_pieces = 'PNBRQK' if board.white_to_move else 'pnbrqk'
    enemy_pieces = 'pnbrqk' if board.white_to_move else 'PNBRQK'
    for square in range(64):
        piece = board.get_piece_at_square(square)
        if piece and piece in own_pieces:
            attackers = get_attackers(board, square, not board.white_to_move)
            if attackers:
                defenders = get_attackers(board, square, board.white_to_move)
                piece_value = abs(PIECE_VALUES.get(piece.upper(), 0))
                if not defenders:
                    score -= piece_value
                else:
                    exchange_score = static_exchange_evaluation(board, piece_value, attackers, defenders)
                    score += exchange_score
    return score

def get_attackers(board, square, by_white):
    attackers = []
    attacking_pieces = 'PNBRQK' if by_white else 'pnbrqk'
    for piece in attacking_pieces:
        bitboard = board.bitboards.get(piece, 0)
        if bitboard:
            from_squares = [i for i in range(64) if bitboard & (1 << i)]
            for from_square in from_squares:
                attacks = board.generate_piece_moves(piece, from_square, attacks_only=True)
                if any(move.to_square == square for move in attacks):
                    attackers.append({'piece': piece, 'from_square': from_square, 'value': abs(PIECE_VALUES.get(piece.upper(), 0))})
    return attackers

def static_exchange_evaluation(board, piece_value, attackers, defenders):
    if board.white_to_move:
        attackers_white = defenders
        attackers_black = attackers
    else:
        attackers_white = attackers
        attackers_black = defenders
    side_to_move = 0 if board.white_to_move else 1
    material_swings = []
    target_value = piece_value
    material_swings.append(target_value if side_to_move == 0 else -target_value)
    attack_lists = [attackers_white, attackers_black]
    side = 1 - side_to_move
    while attack_lists[side]:
        attacker = min(attack_lists[side], key=lambda x: x['value'])
        attack_lists[side].remove(attacker)
        gain = abs(attacker['value'])
        material_swings.append(gain if side == 0 else -gain)
        side = 1 - side
    for i in range(len(material_swings) - 2, -1, -1):
        material_swings[i] = -material_swings[i + 1] - material_swings[i]
    if side_to_move == 0:
        return max(material_swings)
    else:
        return min(material_swings)

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

def is_file_open(board, file):
    for rank in range(8):
        square = rank * 8 + file
        if board.bitboards.get('P', 0) & (1 << square):
            return False
        if board.bitboards.get('p', 0) & (1 << square):
            return False
    return True
