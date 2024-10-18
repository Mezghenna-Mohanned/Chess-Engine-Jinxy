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
    threats_score = 0
    space_score = 0
    initiative_score = 0
    development_score = 0
    imbalances_score = 0
    endgame_score = 0
    opponent_weaknesses_score = 0
    mobility_restrictions_score = 0
    exchange_score = 0

    phase = get_game_phase(board)

    piece_counts = {'B': 0, 'b': 0, 'N': 0, 'n': 0}

    own_pieces = 'PNBRQK' if board.white_to_move else 'pnbrqk'
    enemy_pieces = 'pnbrqk' if board.white_to_move else 'PNBRQK'

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

            mobility = len(board.generate_piece_moves(piece, square))
            if piece.isupper():
                mobility_score += mobility
            else:
                mobility_score -= mobility

            if piece.upper() == 'B':
                piece_counts[piece] += 1
                if is_bad_bishop(board, square, piece.isupper()):
                    positional_score -= 15 if piece.isupper() else -15

            if piece.upper() == 'N':
                piece_counts[piece] += 1
                if is_knight_outpost(board, square, piece.isupper()):
                    knight_outpost_score += 30 if piece.isupper() else -30

            if piece.upper() == 'R':
                file = square % 8
                if is_file_open(board, file):
                    rook_on_open_file_score += 20 if piece.isupper() else -20
                elif is_file_semi_open(board, file, piece.isupper()):
                    rook_on_open_file_score += 10 if piece.isupper() else -10

            if piece.upper() == 'Q':
                queen_mobility_score += mobility if piece.isupper() else -mobility
                if is_queen_exposed(board, square):
                    positional_score -= 20 if piece.isupper() else -20

            if is_trapped_piece(board, piece, square):
                positional_score -= 50 if piece.isupper() else -50

            space_score += evaluate_space(board, piece, square)

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
             queen_mobility_score +
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
            piece_value = abs(PIECE_VALUES[piece])
            total_material += piece_value * bin(bitboard).count('1')
    if total_material > 32000:
        return 'opening'
    elif total_material > 20000:
        return 'middlegame'
    else:
        return 'endgame'


def evaluate_king_safety(board):
    score = 0
    own_king_square = board.find_king_square(board.white_to_move)
    if own_king_square is None:
        return -100000 if board.white_to_move else 100000

    enemy_moves = board.generate_legal_moves()
    attack_zones = get_king_attack_zones(own_king_square)
    attack_score = 0

    for move in enemy_moves:
        if move.to_square in attack_zones:
            attacker_value = get_piece_attack_weight(move.piece)
            attack_score += attacker_value

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

def evaluate_open_files_to_king(board, king_square, is_white):
    score = 0
    file = king_square % 8
    enemy_rooks_queens = board.bitboards.get('r' if is_white else 'R', 0) | board.bitboards.get('q' if is_white else 'Q', 0)
    if is_file_open(board, file):
        while enemy_rooks_queens:
            sq = (enemy_rooks_queens & -enemy_rooks_queens).bit_length() - 1
            if sq % 8 == file:
                score += 30
            enemy_rooks_queens &= enemy_rooks_queens - 1
    return score

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

def evaluate_pawn_structure(board):
    score = 0
    white_pawns = board.bitboards.get('P', 0)
    black_pawns = board.bitboards.get('p', 0)

    score += evaluate_pawn_weaknesses(board, white_pawns, is_white=True)
    score -= evaluate_pawn_weaknesses(board, black_pawns, is_white=False)

    score += evaluate_pawn_islands(board, white_pawns, is_white=True)
    score -= evaluate_pawn_islands(board, black_pawns, is_white=False)

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

def evaluate_pawn_islands(board, pawns, is_white):
    score = 0
    pawn_files = [i for i in range(8) if pawns & FILE_MASKS[i]]
    pawn_islands = 1 if pawn_files else 0
    for i in range(1, len(pawn_files)):
        if pawn_files[i] != pawn_files[i - 1] + 1:
            pawn_islands += 1
    score -= pawn_islands * 15
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
    central_squares = [18, 19, 20, 21, 26, 27, 28, 29, 34, 35, 36, 37, 42, 43, 44, 45]
    own_pieces = 'PNBRQK' if board.white_to_move else 'pnbrqk'
    for piece in own_pieces:
        bitboard = board.bitboards.get(piece, 0)
        piece_value = 0
        if piece.upper() == 'P':
            piece_value = 10
        elif piece.upper() == 'N' or piece.upper() == 'B':
            piece_value = 30
        elif piece.upper() == 'R':
            piece_value = 50
        elif piece.upper() == 'Q':
            piece_value = 90
        while bitboard:
            square = (bitboard & -bitboard).bit_length() - 1
            attacks = board.generate_piece_moves(piece, square, attacks_only=True)
            for move in attacks:
                if move.to_square in central_squares:
                    score += piece_value
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
    own_pawns_copy = own_pawns
    while own_pawns_copy:
        square = (own_pawns_copy & -own_pawns_copy).bit_length() - 1
        file = square % 8
        rank = square // 8
        if is_pawn_passed(board, square, enemy_pawns, is_white):
            distance_to_promotion = 7 - rank if is_white else rank
            base_score = 50 + (distance_to_promotion * 10)
            if is_protected_passed_pawn(board, square, is_white):
                base_score += 30
            score += base_score
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
            captured_value = abs(PIECE_VALUES[move.captured_piece])
            attacker_value = abs(PIECE_VALUES[move.piece])
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

def evaluate_space(board, piece, square):
    score = 0
    rank = square // 8
    is_white = piece.isupper()
    if is_white and rank >= 4:
        score += 5
    elif not is_white and rank <= 3:
        score += 5
    return score

def evaluate_opponent_weaknesses(board):
    score = 0
    enemy_pieces = 'pnbrqk' if board.white_to_move else 'PNBRQK'
    for piece in enemy_pieces:
        bitboard = board.bitboards.get(piece, 0)
        while bitboard:
            square = (bitboard & -bitboard).bit_length() - 1
            if is_piece_undefended(board, piece, square):
                score += 20
            bitboard &= bitboard - 1
    return score

def is_piece_undefended(board, piece, square):
    own_pieces = 'PNBRQK' if piece.islower() else 'pnbrqk'
    for p in own_pieces:
        bitboard = board.bitboards.get(p, 0)
        while bitboard:
            from_square = (bitboard & -bitboard).bit_length() - 1
            attacks = board.generate_piece_moves(p, from_square, attacks_only=True)
            for move in attacks:
                if move.to_square == square:
                    return False
            bitboard &= bitboard - 1
    return True

def evaluate_development(board):
    score = 0
    own_pieces = 'PNBRQ' if board.white_to_move else 'pnbrq'
    for piece in own_pieces:
        bitboard = board.bitboards.get(piece, 0)
        starting_rank = 0 if board.white_to_move else 7
        while bitboard:
            square = (bitboard & -bitboard).bit_length() - 1
            rank = square // 8
            if rank == starting_rank:
                score -= 10
            bitboard &= bitboard - 1
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
        return 0  # Or some large value indicating maximum distance
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
                piece_value = abs(PIECE_VALUES[piece])

                if not defenders:
                    score -= piece_value
                else:
                    exchange_score = static_exchange_evaluation(board, square, piece_value, attackers, defenders)
                    score += exchange_score

    return score

def get_attackers(board, square, by_white):
    attackers = []
    attacking_pieces = 'PNBRQK' if by_white else 'pnbrqk'
    for piece in attacking_pieces:
        bitboard = board.bitboards.get(piece, 0)
        while bitboard:
            from_square = (bitboard & -bitboard).bit_length() - 1
            attacks = board.generate_piece_moves(piece, from_square, attacks_only=True)
            for move in attacks:
                if move.to_square == square:
                    attackers.append({
                        'piece': piece,
                        'from_square': from_square,
                        'value': abs(PIECE_VALUES[piece])
                    })
            bitboard &= bitboard - 1
    return attackers

def static_exchange_evaluation(board, square, piece_value, attackers, defenders):
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

def is_trapped_piece(board, piece, square):
    moves = board.generate_piece_moves(piece, square)
    return len(moves) == 0

def is_file_open(board, file):
    for rank in range(8):
        square = rank * 8 + file
        if board.bitboards.get('P', 0) & (1 << square):
            return False
        if board.bitboards.get('p', 0) & (1 << square):
            return False
    return True

def is_file_semi_open(board, file, is_white):
    own_pawn_piece = 'P' if is_white else 'p'
    enemy_pawn_piece = 'p' if is_white else 'P'
    for rank in range(8):
        square = rank * 8 + file
        if board.bitboards.get(own_pawn_piece, 0) & (1 << square):
            return False
        if board.bitboards.get(enemy_pawn_piece, 0) & (1 << square):
            return True
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

def is_bad_bishop(board, square, is_white):
    pawn_piece = 'P' if is_white else 'p'
    pawn_squares = board.bitboards.get(pawn_piece, 0)
    color = (square // 8 + square % 8) % 2
    while pawn_squares:
        pawn_square = (pawn_squares & -pawn_squares).bit_length() - 1
        pawn_color = (pawn_square // 8 + pawn_square % 8) % 2
        if pawn_color == color:
            return True
        pawn_squares &= pawn_squares - 1
    return False

def is_queen_exposed(board, square):
    rank = square // 8
    if rank == 0 or rank == 7:
        return False
    return True

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
