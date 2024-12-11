import numpy as np
from functools import lru_cache
from src.core.constants import PIECE_VALUES, POSITIONAL_VALUES, FILE_MASKS


PIECE_SQUARE_TABLES = {
    'P': np.array([
         0,   5,   5,   0,   5,  10,  50,   0,
         0,  10,  -5,   0,   5,  10,  50,   0,
         0,   0,   0,  20,  10,  20,  50,   0,
         0,   0,   0,  25,  25,  20,  50,   0,
         0,   5,  10,  25,  25,  20,  50,   0,
         0,   5,  10,   0,   0, -10,  50,   0,
         0,  10,  10, -20, -20,  10,  50,   0,
         0,   5,   5,   0,   5,  10,  50,   0,
    ]),
    'N': np.array([
        -50, -40, -30, -30, -30, -30, -40, -50,
        -40, -20,   0,   0,   0,   0, -20, -40,
        -30,   0,  15,  15,  15,  15,   0, -30,
        -30,   5,  15,  20,  20,  15,   5, -30,
        -30,   0,  15,  20,  20,  15,   0, -30,
        -30,   5,  15,  15,  15,  15,   5, -30,
        -40, -20,   0,   5,   5,   0, -20, -40,
        -50, -40, -30, -30, -30, -30, -40, -50,
    ]),
    'B': np.array([
        -20, -10, -10, -10, -10, -10, -10, -20,
        -10,   5,   0,   0,   0,   0,   5, -10,
        -10,  10,  10,  10,  10,  10,  10, -10,
        -10,   0,  10,  15,  15,  10,   0, -10,
        -10,   5,  10,  15,  15,  10,   5, -10,
        -10,   0,  10,  10,  10,  10,   0, -10,
        -10,   5,   0,   0,   0,   0,   5, -10,
        -20, -10, -10, -10, -10, -10, -10, -20,
    ]),
    'R': np.array([
         0,   0,   5,  10,  10,   5,   0,   0,
        -5,   0,   0,   0,   0,   0,   0,  -5,
        -5,   0,   0,   0,   0,   0,   0,  -5,
        -5,   0,   0,   5,   5,   0,   0,  -5,
        -5,   0,   0,   5,   5,   0,   0,  -5,
        -5,   0,   0,   0,   0,   0,   0,  -5,
         5,  10,  10,  10,  10,  10,  10,   5,
         0,   0,   0,   5,   5,   0,   0,   0,
    ]),
    'Q': np.array([
        -20, -10, -10,  -5,  -5, -10, -10, -20,
        -10,   0,   0,   0,   0,   5,   0, -10,
        -10,   0,   5,   5,   5,   5,   5, -10,
         -5,   0,   5,   5,   5,   5,   0,  -5,
          0,   0,   5,   5,   5,   5,   0,  -5,
        -10,   5,   5,   5,   5,   5,   0, -10,
        -10,   0,   5,   0,   0,   0,   0, -10,
        -20, -10, -10,  -5,  -5, -10, -10, -20,
    ]),
    'K': np.array([
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -20, -30, -30, -40, -40, -30, -30, -20,
        -10, -20, -20, -20, -20, -20, -20, -10,
         20,  20,   0,   0,   0,   0,  20,  20,
         20,  30,  10,   0,   0,  10,  30,  20,
    ]),
}

@lru_cache(maxsize=None)
def evaluate(board):
    """
    Evaluates the board state and returns a score from the perspective of the player to move.
    Positive scores favor White, negative scores favor Black.
    """
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
    own_pieces = 'PNBRQK' if board.white_to_move else 'pnbrqk'
    enemy_pieces = 'pnbrqk' if board.white_to_move else 'PNBRQK'

    # Initialize piece counts for bishop pair evaluation
    own_bishops = 0
    enemy_bishops = 0

    # Evaluate own pieces
    for piece in own_pieces:
        bitboard = board.bitboards.get(piece, 0)
        piece_value = PIECE_VALUES.get(piece.upper(), 0)
        if bitboard:
            squares = board.get_squares_from_bitboard(bitboard)
            material_score += piece_value * len(squares)

            # Positional score using piece-square tables
            if piece.upper() in PIECE_SQUARE_TABLES:
                table = PIECE_SQUARE_TABLES[piece.upper()]
                positional_score += np.sum(table[squares])

            # Mobility
            own_mobility = sum(len(board.generate_piece_moves(piece, sq)) for sq in squares)
            mobility_score += own_mobility

            # Space
            space_score += evaluate_space(piece, squares, own=True)

            # Count bishops for bishop pair
            if piece.upper() == 'B':
                own_bishops += len(squares)

            # Development
            development_score += evaluate_development_piece(piece, squares)

            # Knight outposts
            if piece.upper() == 'N':
                knight_outpost_score += evaluate_knight_outposts(board, piece, squares)

            # Rook on open file
            if piece.upper() == 'R':
                rook_on_open_file_score += evaluate_rook_on_open_file(board, piece, squares)

    # Evaluate enemy pieces
    for piece in enemy_pieces:
        bitboard = board.bitboards.get(piece, 0)
        piece_value = PIECE_VALUES.get(piece.upper(), 0)
        if bitboard:
            squares = board.get_squares_from_bitboard(bitboard)
            material_score -= piece_value * len(squares)

            # Positional score using piece-square tables (flipped for opponent)
            if piece.upper() in PIECE_SQUARE_TABLES:
                table = PIECE_SQUARE_TABLES[piece.upper()][::-1]
                positional_score -= np.sum(table[squares])

            # Mobility
            enemy_mobility = sum(len(board.generate_piece_moves(piece, sq)) for sq in squares)
            mobility_score -= enemy_mobility

            # Space
            space_score -= evaluate_space(piece, squares, own=False)
            if piece.upper() == 'B':
                enemy_bishops += len(squares)


            development_score -= evaluate_development_piece(piece, squares)

            if piece.upper() == 'N':
                knight_outpost_score -= evaluate_knight_outposts(board, piece, squares)

            if piece.upper() == 'R':
                rook_on_open_file_score -= evaluate_rook_on_open_file(board, piece, squares)

    if own_bishops >= 2:
        bishop_pair_score += 50
    if enemy_bishops >= 2:
        bishop_pair_score -= 50

    king_safety_score = evaluate_king_safety(board)
    pawn_structure_score = evaluate_pawn_structure(board)
    center_control_score = evaluate_center_control(board)
    piece_coordination_score = evaluate_piece_coordination(board)
    passed_pawn_score = evaluate_passed_pawns(board)
    threats_score = evaluate_threats(board)
    opponent_weaknesses_score = evaluate_opponent_weaknesses(board)
    exchange_score = evaluate_exchanges(board)

    score = (
        material_score +
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
        exchange_score
    )

    if phase == 'endgame':
        endgame_score = evaluate_endgame(board)
        score += endgame_score
    if not board.white_to_move:
        score = -score

    return score

def get_game_phase(board):
    """
    Determines the current phase of the game based on material.
    """
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
    """
    Counts the number of legal moves available to a piece for mobility evaluation.
    """
    mobility = 0
    for square in squares:
        moves = board.generate_piece_moves(piece, square)
        mobility += len(moves)
    return mobility

def evaluate_space(piece, squares, own=True):
    """
    Evaluates space control based on piece positions.
    """
    score = 0
    ranks = np.array(squares) // 8
    if own:
        if piece.isupper():
            score += np.sum(ranks >= 4) * 5
        else:
            score += np.sum(ranks <= 3) * 5
    else:
        if piece.isupper():
            score -= np.sum(ranks >= 4) * 5
        else:
            score -= np.sum(ranks <= 3) * 5
    return score

def evaluate_king_safety(board):
    """
    Evaluates the safety of the king based on surrounding pieces and enemy threats.
    """
    score = 0
    own_king_square = board.find_king_square(board.white_to_move)
    if own_king_square is None:
        return -100000 if board.white_to_move else 100000

    enemy_moves = board.generate_legal_moves(simulate=False, own=False)
    attack_zones = get_king_attack_zones(own_king_square)
    attack_score = sum(get_piece_attack_weight(move.piece) for move in enemy_moves if move.to_square in attack_zones)
    shield_penalty = evaluate_king_pawn_shield(board, own_king_square, board.white_to_move)
    open_file_penalty = evaluate_open_files_to_king(board, own_king_square, board.white_to_move)

    score -= attack_score * 10
    score -= shield_penalty
    score -= open_file_penalty
    return score

def get_king_attack_zones(king_square):
    """
    Returns a set of squares that are adjacent to the king for threat evaluation.
    """
    adjacent = get_adjacent_squares(king_square)
    return set(adjacent)

def evaluate_king_pawn_shield(board, king_square, is_white):
    """
    Evaluates the pawn shield around the king.
    """
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
                    score += 10
    return score

def evaluate_open_files_to_king(board, king_square, is_white):
    """
    Penalizes enemy control over open files near the king.
    """
    score = 0
    file = king_square % 8
    enemy_rooks_queens = board.bitboards.get('r' if is_white else 'R', 0) | board.bitboards.get('q' if is_white else 'Q', 0)
    if is_file_open(board, file):
        enemy_pieces = board.get_squares_from_bitboard(enemy_rooks_queens)
        if any(sq % 8 == file for sq in enemy_pieces):
            score += 30
    return score

def get_piece_attack_weight(piece):
    """
    Assigns weights based on the type of piece threatening the king.
    """
    piece = piece.upper()
    weights = {'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9}
    return weights.get(piece, 0)

def evaluate_pawn_structure(board):
    """
    Evaluates the pawn structure for potential weaknesses or strengths.
    """
    score = 0
    white_pawns = board.bitboards.get('P', 0)
    black_pawns = board.bitboards.get('p', 0)
    score += evaluate_pawn_weaknesses(white_pawns, is_white=True)
    score -= evaluate_pawn_weaknesses(black_pawns, is_white=False)
    return score

def evaluate_pawn_weaknesses(pawns, is_white):
    """
    Evaluates pawn weaknesses such as doubled and isolated pawns.
    """
    score = 0
    files = [i % 8 for i in range(64) if pawns & (1 << i)]
    unique_files = set(files)
    counts = {f: files.count(f) for f in unique_files}

    for file, count in counts.items():
        if count > 1:
            score -= (count - 1) * 30

        is_isolated = True
        for neighbor_file in [file - 1, file + 1]:
            if neighbor_file in unique_files:
                is_isolated = False
                break
        if is_isolated:
            score -= 25

    score -= evaluate_backward_pawns(pawns, is_white)

    return score

def evaluate_backward_pawns(pawns, is_white):
    """
    Evaluates backward pawns.
    """
    return 0

def evaluate_center_control(board):
    """
    Evaluates control over the central squares.
    """
    score = 0
    central_squares = [27, 28, 35, 36]  # D4, E4, D5, E5
    own_pieces = 'PNBRQK' if board.white_to_move else 'pnbrqk'
    for piece in own_pieces:
        bitboard = board.bitboards.get(piece, 0)
        if bitboard:
            squares = board.get_squares_from_bitboard(bitboard)
            for square in squares:
                if square in central_squares:
                    score += 20
                attacks = board.generate_piece_moves(piece, square, attacks_only=True)
                for move in attacks:
                    if move.to_square in central_squares:
                        score += 10
    return score

def evaluate_piece_coordination(board):
    """
    Evaluates how well pieces are coordinating with each other.
    """
    score = 0
    own_pieces = 'PNBRQK' if board.white_to_move else 'pnbrqk'
    for piece in own_pieces:
        bitboard = board.bitboards.get(piece, 0)
        if bitboard:
            squares = board.get_squares_from_bitboard(bitboard)
            for from_square in squares:
                attacks = board.generate_piece_moves(piece, from_square, attacks_only=True)
                for move in attacks:
                    target_piece = board.get_piece_at_square(move.to_square)
                    if target_piece and target_piece in own_pieces:
                        score += 10
    return score

def evaluate_passed_pawns(board):
    """
    Evaluates the presence of passed pawns.
    """
    score = 0
    white_pawns = board.bitboards.get('P', 0)
    black_pawns = board.bitboards.get('p', 0)
    score += evaluate_passed_pawns_for_color(white_pawns, black_pawns, is_white=True)
    score -= evaluate_passed_pawns_for_color(black_pawns, white_pawns, is_white=False)
    return score

def evaluate_passed_pawns_for_color(own_pawns, enemy_pawns, is_white):
    """
    Counts and scores passed pawns for a given color.
    """
    score = 0
    own_pawn_squares = [i for i in range(64) if own_pawns & (1 << i)]
    for square in own_pawn_squares:
        if is_pawn_passed(square, enemy_pawns, is_white):
            rank = square // 8
            distance = 7 - rank if is_white else rank
            base_score = 50 + (7 - distance) * 10
            score += base_score
    return score

def is_pawn_passed(square, enemy_pawns, is_white):
    """
    Determines if a pawn is passed.
    """
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

def evaluate_threats(board):
    """
    Evaluates threats posed by own pieces.
    """
    score = 0
    own_moves = board.generate_legal_moves(simulate=False)
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
    """
    Determines if a move is threatening an enemy piece.
    """
    target_piece = board.get_piece_at_square(move.to_square)
    if target_piece and target_piece.islower() != move.piece.islower():
        return True
    return False

def evaluate_opponent_weaknesses(board):
    """
    Evaluates weaknesses in the opponent's position.
    """
    score = 0
    enemy_pieces = 'pnbrqk' if board.white_to_move else 'PNBRQK'
    for piece in enemy_pieces:
        bitboard = board.bitboards.get(piece, 0)
        if bitboard:
            squares = board.get_squares_from_bitboard(bitboard)
            for square in squares:
                if is_piece_undefended(board, square, own=False):
                    score += 20
    return score

def is_piece_undefended(board, square, own=True):
    """
    Checks if a piece at a given square is undefended.
    """
    own_pieces = 'PNBRQK' if (board.white_to_move == own) else 'pnbrqk'
    for piece in own_pieces:
        bitboard = board.bitboards.get(piece, 0)
        if bitboard:
            from_squares = board.get_squares_from_bitboard(bitboard)
            for from_square in from_squares:
                attacks = board.generate_piece_moves(piece, from_square, attacks_only=True)
                if any(move.to_square == square for move in attacks):
                    return False
    return True



def evaluate_development(board):
    """
    Evaluates the development of pieces.
    """
    return 0


"""
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
"""


def evaluate_development_piece(piece, squares):
    """
    Evaluates development for individual pieces.
    """
    score = 0
    starting_rank = 0 if piece.isupper() else 7
    for square in squares:
        rank = square // 8
        if rank != starting_rank:
            score += 10  # Bonus for developed pieces
    return score

def evaluate_knight_outposts(board, piece, squares):
    """
    Evaluates knight outposts.
    """
    score = 0
    for square in squares:
        if is_knight_outpost(board, square, piece):
            score += 30
    return score

def is_knight_outpost(board, square, piece):
    """
    Checks if a knight is on an outpost.
    """
    rank = square // 8
    file = square % 8
    if (rank >= 4 and piece.isupper()) or (rank <= 3 and piece.islower()):
        enemy_pawns = board.bitboards.get('p' if piece.isupper() else 'P', 0)
        for df in [-1, 1]:
            f = file + df
            if 0 <= f < 8:
                for r in range(8):
                    sq = r * 8 + f
                    if enemy_pawns & (1 << sq):
                        return False
        return True
    return False

def evaluate_rook_on_open_file(board, piece, squares):
    """
    Evaluates rooks on open files.
    """
    score = 0
    for square in squares:
        file = square % 8
        if is_file_open(board, file):
            score += 20
    return score

def is_file_open(board, file):
    """
    Checks if a file is open (no pawns of either color).
    """
    for rank in range(8):
        square = rank * 8 + file
        if board.bitboards.get('P', 0) & (1 << square):
            return False
        if board.bitboards.get('p', 0) & (1 << square):
            return False
    return True

def evaluate_endgame(board):
    """
    Additional evaluation for the endgame phase.
    """
    score = 0
    own_king_square = board.find_king_square(board.white_to_move)
    enemy_king_square = board.find_king_square(not board.white_to_move)
    own_king_distance = manhattan_distance(own_king_square, enemy_king_square)
    score += (14 - own_king_distance) * 10  # Encourage bringing the king closer
    return score

def manhattan_distance(sq1, sq2):
    """
    Calculates the Manhattan distance between two squares.
    """
    if sq1 is None or sq2 is None:
        return 0
    rank1, file1 = divmod(sq1, 8)
    rank2, file2 = divmod(sq2, 8)
    return abs(rank1 - rank2) + abs(file1 - file2)

def evaluate_exchanges(board):
    """
    Evaluates potential exchanges.
    """
    # Implemented as part of threats and opponent weaknesses
    return 0

def get_adjacent_squares(square):
    """
    Returns a list of squares adjacent to the given square.
    """
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
