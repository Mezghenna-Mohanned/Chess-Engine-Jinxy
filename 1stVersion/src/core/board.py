from src.core.constants import INITIAL_POSITIONS, FILE_MASKS
import random
import json
from src.utils.utils import algebraic_to_square, square_to_algebraic
from src.ml.predict_move import MovePredictor
from src.Ai.minimax import find_best_move
from src.Ai.evaluation import evaluate

class Board:
    def __init__(self):
        self.bitboards = INITIAL_POSITIONS.copy()
        self.white_to_move = True
        self.castling_rights = {'K': True, 'Q': True, 'k': True, 'q': True}
        self.en_passant_target = None
        self.halfmove_clock = 0
        self.fullmove_number = 1
        self.move_history = []

        self.update_occupied()

        random.seed(0)
        pieces = ['P', 'N', 'B', 'R', 'Q', 'K',
                  'p', 'n', 'b', 'r', 'q', 'k']

        self.zobrist_piece_keys = {
            piece: [random.getrandbits(64) for _ in range(64)] for piece in pieces
        }

        self.zobrist_castling_keys = {
            'K': random.getrandbits(64),
            'Q': random.getrandbits(64),
            'k': random.getrandbits(64),
            'q': random.getrandbits(64)
        }

        self.zobrist_en_passant_keys = [random.getrandbits(64) for _ in range(8)]
        self.zobrist_side_key = random.getrandbits(64)
        self.zobrist_hash = self.compute_zobrist_hash()

        self.move_predictor = MovePredictor()

    def compute_zobrist_hash(self):
        zobrist_hash = 0
        for piece, bitboard in self.bitboards.items():
            squares = self.get_squares_from_bitboard(bitboard)
            for square in squares:
                zobrist_hash ^= self.zobrist_piece_keys[piece][square]

        for right in ['K', 'Q', 'k', 'q']:
            if self.castling_rights.get(right, False):
                zobrist_hash ^= self.zobrist_castling_keys[right]

        if self.en_passant_target is not None:
            zobrist_hash ^= self.zobrist_en_passant_keys[self.en_passant_target % 8]

        if self.white_to_move:
            zobrist_hash ^= self.zobrist_side_key

        return zobrist_hash

    def get_squares_from_bitboard(self, bitboard):
        squares = []
        while bitboard:
            lsb = bitboard & -bitboard
            square = (lsb).bit_length() - 1
            squares.append(square)
            bitboard &= bitboard - 1
        return squares

    def update_occupied(self):
        self.occupied_white = 0
        self.occupied_black = 0
        for piece, bitboard in self.bitboards.items():
            if piece.isupper():
                self.occupied_white |= bitboard
            else:
                self.occupied_black |= bitboard
        self.occupied = self.occupied_white | self.occupied_black

    def make_move(self, move, change_turn=True):
        self.move_history.append({
            'from_square': move.from_square,
            'to_square': move.to_square,
            'promoted_piece': move.promoted_piece if hasattr(move, 'promoted_piece') else None,
            'captured_piece': move.captured_piece if hasattr(move, 'captured_piece') else None,
            'is_en_passant': move.is_en_passant if hasattr(move, 'is_en_passant') else False,
            'is_castling': move.is_castling if hasattr(move, 'is_castling') else False,
            'bitboards': self.bitboards.copy(),
            'white_to_move': self.white_to_move,
            'castling_rights': self.castling_rights.copy(),
            'en_passant_target': self.en_passant_target,
            'halfmove_clock': self.halfmove_clock,
            'fullmove_number': self.fullmove_number,
            'zobrist_hash': self.zobrist_hash,
        })

        self.zobrist_hash ^= self.zobrist_side_key

        piece = move.piece
        from_square = move.from_square
        to_square = move.to_square

        self.bitboards[piece] &= ~(1 << from_square)
        self.zobrist_hash ^= self.zobrist_piece_keys[piece][from_square]

        captured_piece = self.get_piece_at_square(to_square) if self.is_square_occupied_by_opponent(to_square) else None

        if captured_piece:
            self.bitboards[captured_piece] &= ~(1 << to_square)
            self.zobrist_hash ^= self.zobrist_piece_keys[captured_piece][to_square]
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        if move.promoted_piece:
            promoted_piece = move.promoted_piece
            self.bitboards[promoted_piece] |= (1 << to_square)
            self.zobrist_hash ^= self.zobrist_piece_keys[promoted_piece][to_square]
        else:
            self.bitboards[piece] |= (1 << to_square)
            self.zobrist_hash ^= self.zobrist_piece_keys[piece][to_square]

        if move.is_en_passant:
            ep_capture_square = to_square + (8 if self.white_to_move else -8)
            captured_pawn = 'p' if self.white_to_move else 'P'
            self.bitboards[captured_pawn] &= ~(1 << ep_capture_square)
            self.zobrist_hash ^= self.zobrist_piece_keys[captured_pawn][ep_capture_square]
            captured_piece = captured_pawn
            self.halfmove_clock = 0

        if move.is_castling:
            if to_square == 6:
                self.bitboards['R'] &= ~(1 << 7)
                self.bitboards['R'] |= (1 << 5)
                self.zobrist_hash ^= self.zobrist_piece_keys['R'][7]
                self.zobrist_hash ^= self.zobrist_piece_keys['R'][5]
            elif to_square == 2:
                self.bitboards['R'] &= ~(1 << 0)
                self.bitboards['R'] |= (1 << 3)
                self.zobrist_hash ^= self.zobrist_piece_keys['R'][0]
                self.zobrist_hash ^= self.zobrist_piece_keys['R'][3]
            elif to_square == 62:
                # Black king-side castling
                self.bitboards['r'] &= ~(1 << 63)
                self.bitboards['r'] |= (1 << 61)
                self.zobrist_hash ^= self.zobrist_piece_keys['r'][63]
                self.zobrist_hash ^= self.zobrist_piece_keys['r'][61]
            elif to_square == 58:
                # Black queen-side castling
                self.bitboards['r'] &= ~(1 << 56)
                self.bitboards['r'] |= (1 << 59)
                self.zobrist_hash ^= self.zobrist_piece_keys['r'][56]
                self.zobrist_hash ^= self.zobrist_piece_keys['r'][59]

        self.update_castling_rights(piece, from_square, to_square)

        if self.en_passant_target is not None:
            self.zobrist_hash ^= self.zobrist_en_passant_keys[self.en_passant_target % 8]
            self.en_passant_target = None

        if piece.upper() == 'P' and abs(to_square - from_square) == 16:
            self.en_passant_target = (from_square + to_square) // 2
            self.zobrist_hash ^= self.zobrist_en_passant_keys[self.en_passant_target % 8]

        if piece.upper() == 'P' or captured_piece:
            self.halfmove_clock = 0

        if not self.white_to_move:
            self.fullmove_number += 1

        self.update_occupied()

        if change_turn:
            self.white_to_move = not self.white_to_move

    def undo_move(self, move):
        if not self.move_history:
            return
        state = self.move_history.pop()
        self.bitboards = state['bitboards']
        self.white_to_move = state['white_to_move']
        self.castling_rights = state['castling_rights']
        self.en_passant_target = state['en_passant_target']
        self.halfmove_clock = state['halfmove_clock']
        self.fullmove_number = state['fullmove_number']
        self.zobrist_hash = state['zobrist_hash']

        self.update_occupied()

    def update_castling_rights(self, piece, from_square, to_square):
        if piece == 'K':
            if self.castling_rights['K']:
                self.zobrist_hash ^= self.zobrist_castling_keys['K']
            if self.castling_rights['Q']:
                self.zobrist_hash ^= self.zobrist_castling_keys['Q']
            self.castling_rights['K'] = False
            self.castling_rights['Q'] = False
        elif piece == 'k':
            if self.castling_rights['k']:
                self.zobrist_hash ^= self.zobrist_castling_keys['k']
            if self.castling_rights['q']:
                self.zobrist_hash ^= self.zobrist_castling_keys['q']
            self.castling_rights['k'] = False
            self.castling_rights['q'] = False
        elif piece == 'R':
            if from_square == 0 and self.castling_rights['Q']:
                self.zobrist_hash ^= self.zobrist_castling_keys['Q']
                self.castling_rights['Q'] = False
            elif from_square == 7 and self.castling_rights['K']:
                self.zobrist_hash ^= self.zobrist_castling_keys['K']
                self.castling_rights['K'] = False
        elif piece == 'r':
            if from_square == 56 and self.castling_rights['q']:
                self.zobrist_hash ^= self.zobrist_castling_keys['q']
                self.castling_rights['q'] = False
            elif from_square == 63 and self.castling_rights['k']:
                self.zobrist_hash ^= self.zobrist_castling_keys['k']
                self.castling_rights['k'] = False

        if self.is_square_occupied_by_opponent(to_square):
            captured_piece = self.get_piece_at_square(to_square)
            if captured_piece == 'R':
                if to_square == 0 and self.castling_rights['Q']:
                    self.zobrist_hash ^= self.zobrist_castling_keys['Q']
                    self.castling_rights['Q'] = False
                elif to_square == 7 and self.castling_rights['K']:
                    self.zobrist_hash ^= self.zobrist_castling_keys['K']
                    self.castling_rights['K'] = False
            elif captured_piece == 'r':
                if to_square == 56 and self.castling_rights['q']:
                    self.zobrist_hash ^= self.zobrist_castling_keys['q']
                    self.castling_rights['q'] = False
                elif to_square == 63 and self.castling_rights['k']:
                    self.zobrist_hash ^= self.zobrist_castling_keys['k']
                    self.castling_rights['k'] = False

    def is_square_occupied_by_opponent(self, square):
        if self.white_to_move:
            return bool(self.occupied_black & (1 << square))
        else:
            return bool(self.occupied_white & (1 << square))

    def is_game_over(self):
        if self.is_checkmate():
            return True
        if self.is_stalemate():
            return True
        return False

    def is_checkmate(self):
        if not self.is_in_check():
            return False
        legal_moves = self.generate_legal_moves()
        return len(legal_moves) == 0

    def is_stalemate(self):
        if self.is_in_check():
            return False
        legal_moves = self.generate_legal_moves()
        return len(legal_moves) == 0

    def is_in_check(self):
        king_square = self.find_king_square(self.white_to_move)
        if king_square is None:
            return False
        return self.is_square_attacked(king_square, not self.white_to_move)

    def find_king_square(self, is_white):
        king_piece = 'K' if is_white else 'k'
        king_bitboard = self.bitboards.get(king_piece, 0)
        if king_bitboard:
            return (king_bitboard & -king_bitboard).bit_length() - 1
        else:
            return None

    def is_square_attacked(self, square, by_white):
        if by_white:
            for piece in 'PNBRQK':
                bitboard = self.bitboards.get(piece, 0)
                while bitboard:
                    from_square = (bitboard & -bitboard).bit_length() - 1
                    moves = self.generate_piece_moves(piece, from_square, attacks_only=True)
                    for move in moves:
                        if move.to_square == square:
                            return True
                    bitboard &= bitboard - 1
        else:
            for piece in 'pnbrqk':
                bitboard = self.bitboards.get(piece, 0)
                while bitboard:
                    from_square = (bitboard & -bitboard).bit_length() - 1
                    moves = self.generate_piece_moves(piece, from_square, attacks_only=True)
                    for move in moves:
                        if move.to_square == square:
                            return True
                    bitboard &= bitboard - 1
        return False

    def generate_piece_moves(self, piece, from_square, attacks_only=False):
        moves = []
        from_square = int(from_square)
        if piece.upper() == 'P':
            moves.extend(self._generate_pawn_moves(piece, from_square, attacks_only))
        elif piece.upper() == 'N':
            moves.extend(self._generate_knight_moves(piece, from_square, attacks_only))
        elif piece.upper() == 'B':
            moves.extend(self._generate_bishop_moves(piece, from_square, attacks_only))
        elif piece.upper() == 'R':
            moves.extend(self._generate_rook_moves(piece, from_square, attacks_only))
        elif piece.upper() == 'Q':
            moves.extend(self._generate_queen_moves(piece, from_square, attacks_only))
        elif piece.upper() == 'K':
            moves.extend(self._generate_king_moves(piece, from_square, attacks_only))
        return moves

    def generate_legal_moves(self, simulate=True, own=True):
        
        legal_moves = []
        all_moves = []
        if own:
            pieces = 'PNBRQK' if self.white_to_move else 'pnbrqk'
        else:
            pieces = 'pnbrqk' if self.white_to_move else 'PNBRQK'

        for piece in pieces:
            bitboard = self.bitboards.get(piece, 0)
            while bitboard:
                from_square = (bitboard & -bitboard).bit_length() - 1
                moves = self.generate_piece_moves(piece, from_square)
                all_moves.extend(moves)
                bitboard &= bitboard - 1

        if simulate:
            for move in all_moves:
                self.make_move(move, change_turn=False)
                if not self.is_in_check():
                    legal_moves.append(move)
                self.undo_move(move)
        else:
            legal_moves = all_moves

        return legal_moves


    def _generate_pawn_moves(self, piece, from_square, attacks_only=False):
        moves = []
        direction = 8 if piece.isupper() else -8
        start_rank = 1 if piece.isupper() else 6
        promotion_rank = 7 if piece.isupper() else 0
        enemy_pieces = self.occupied_black if piece.isupper() else self.occupied_white
        own_pieces = self.occupied_white if piece.isupper() else self.occupied_black

        for capture_direction in [-1, 1]:
            to_square = from_square + direction + capture_direction
            if 0 <= to_square < 64 and abs((from_square % 8) - (to_square % 8)) == 1:
                is_promotion = to_square // 8 == promotion_rank
                is_en_passant = (to_square == self.en_passant_target)
                if (enemy_pieces & (1 << to_square)) or is_en_passant:
                    captured_piece = (
                        self.get_piece_at_square(to_square)
                        if enemy_pieces & (1 << to_square)
                        else ('p' if piece.isupper() else 'P')
                    )
                    if is_promotion:
                        for promotion_piece in ['Q', 'R', 'B', 'N']:
                            prom_piece = promotion_piece if piece.isupper() else promotion_piece.lower()
                            moves.append(Move(
                                piece, from_square, to_square,
                                captured_piece=captured_piece,
                                promoted_piece=prom_piece,
                                is_en_passant=is_en_passant
                            ))
                    else:
                        moves.append(Move(
                            piece, from_square, to_square,
                            captured_piece=captured_piece,
                            is_en_passant=is_en_passant
                        ))
                elif attacks_only:
                    moves.append(Move(piece, from_square, to_square))

        if attacks_only:
            return moves

        # Forward move
        to_square = from_square + direction
        if 0 <= to_square < 64 and not (self.occupied & (1 << to_square)):
            is_promotion = to_square // 8 == promotion_rank
            if is_promotion:
                for promotion_piece in ['Q', 'R', 'B', 'N']:
                    prom_piece = promotion_piece if piece.isupper() else promotion_piece.lower()
                    moves.append(Move(
                        piece, from_square, to_square,
                        promoted_piece=prom_piece
                    ))
            else:
                moves.append(Move(piece, from_square, to_square))
                # Double move from starting position
                if from_square // 8 == start_rank:
                    to_square2 = from_square + 2 * direction
                    if not (self.occupied & (1 << to_square2)) and not (self.occupied & (1 << (from_square + direction))):
                        moves.append(Move(piece, from_square, to_square2))

        return moves

    def _generate_knight_moves(self, piece, from_square, attacks_only=False):
        moves = []
        knight_offsets = [17, 15, 10, 6, -6, -10, -15, -17]
        own_pieces = self.occupied_white if piece.isupper() else self.occupied_black

        for offset in knight_offsets:
            to_square = from_square + offset
            if 0 <= to_square < 64:
                from_file = from_square % 8
                to_file = to_square % 8
                if abs(from_file - to_file) in [1, 2]:
                    if not (own_pieces & (1 << to_square)):
                        moves.append(Move(piece, from_square, to_square))
        return moves

    def _generate_bishop_moves(self, piece, from_square, attacks_only=False):
        moves = []
        own_pieces = self.occupied_white if piece.isupper() else self.occupied_black
        directions = [9, 7, -7, -9]

        for direction in directions:
            to_square = from_square
            while True:
                to_square += direction
                if 0 <= to_square < 64:
                    from_rank = from_square // 8
                    from_file = from_square % 8
                    to_rank = to_square // 8
                    to_file = to_square % 8
                    if abs(to_rank - from_rank) != abs(to_file - from_file):
                        break
                    if own_pieces & (1 << to_square):
                        if attacks_only:
                            moves.append(Move(piece, from_square, to_square))
                        break
                    moves.append(Move(piece, from_square, to_square))
                    if self.occupied & (1 << to_square):
                        break
                else:
                    break
        return moves

    def _generate_rook_moves(self, piece, from_square, attacks_only=False):
        moves = []
        own_pieces = self.occupied_white if piece.isupper() else self.occupied_black
        directions = [8, -8, 1, -1]

        for direction in directions:
            to_square = from_square
            while True:
                to_square += direction
                if 0 <= to_square < 64:
                    if direction in [1, -1]:
                        from_rank = from_square // 8
                        to_rank = to_square // 8
                        if from_rank != to_rank:
                            break
                    if own_pieces & (1 << to_square):
                        if attacks_only:
                            moves.append(Move(piece, from_square, to_square))
                        break
                    moves.append(Move(piece, from_square, to_square))
                    if self.occupied & (1 << to_square):
                        break
                else:
                    break
        return moves

    def _generate_queen_moves(self, piece, from_square, attacks_only=False):
        moves = []
        moves.extend(self._generate_bishop_moves(piece, from_square, attacks_only))
        moves.extend(self._generate_rook_moves(piece, from_square, attacks_only))
        return moves

    def _generate_king_moves(self, piece, from_square, attacks_only=False):
        moves = []
        king_offsets = [8, -8, 1, -1, 9, 7, -7, -9]
        own_pieces = self.occupied_white if piece.isupper() else self.occupied_black

        for offset in king_offsets:
            to_square = from_square + offset
            if 0 <= to_square < 64:
                from_file = from_square % 8
                to_file = to_square % 8
                if abs(from_file - to_file) <= 1:
                    if not (own_pieces & (1 << to_square)):
                        moves.append(Move(piece, from_square, to_square))
        if not attacks_only:
            moves.extend(self._generate_castling_moves(piece, from_square))
        return moves

    def _generate_castling_moves(self, piece, from_square):
        moves = []
        if self.is_in_check():
            return moves
        if piece.isupper():
            king_side = self.castling_rights.get('K', False)
            queen_side = self.castling_rights.get('Q', False)
            enemy_attacks = self.get_all_attacked_squares(not self.white_to_move)
            if king_side:
                if not self.occupied & (1 << 5) and not self.occupied & (1 << 6):
                    if not any(sq in enemy_attacks for sq in [4, 5, 6]):
                        moves.append(Move(piece, from_square, 6, is_castling=True))
            if queen_side:
                if not self.occupied & (1 << 1) and not self.occupied & (1 << 2) and not self.occupied & (1 << 3):
                    if not any(sq in enemy_attacks for sq in [2, 3, 4]):
                        moves.append(Move(piece, from_square, 2, is_castling=True))
        else:
            king_side = self.castling_rights.get('k', False)
            queen_side = self.castling_rights.get('q', False)
            enemy_attacks = self.get_all_attacked_squares(not self.white_to_move)
            if king_side:
                if not self.occupied & (1 << 61) and not self.occupied & (1 << 62):
                    if not any(sq in enemy_attacks for sq in [60, 61, 62]):
                        moves.append(Move(piece, from_square, 62, is_castling=True))
            if queen_side:
                if not self.occupied & (1 << 57) and not self.occupied & (1 << 58) and not self.occupied & (1 << 59):
                    if not any(sq in enemy_attacks for sq in [58, 59, 60]):
                        moves.append(Move(piece, from_square, 58, is_castling=True))
        return moves

    def get_all_attacked_squares(self, by_white):
        attacked_squares = set()
        if by_white:
            for piece in 'PNBRQK':
                bitboard = self.bitboards.get(piece, 0)
                while bitboard:
                    from_square = (bitboard & -bitboard).bit_length() - 1
                    moves = self.generate_piece_moves(piece, from_square, attacks_only=True)
                    for move in moves:
                        attacked_squares.add(move.to_square)
                    bitboard &= bitboard - 1
        else:
            for piece in 'pnbrqk':
                bitboard = self.bitboards.get(piece, 0)
                while bitboard:
                    from_square = (bitboard & -bitboard).bit_length() - 1
                    moves = self.generate_piece_moves(piece, from_square, attacks_only=True)
                    for move in moves:
                        attacked_squares.add(move.to_square)
                    bitboard &= bitboard - 1
        return attacked_squares

    def get_piece_at_square(self, square):
        for piece, bitboard in self.bitboards.items():
            if bitboard & (1 << square):
                return piece
        return None

    def is_capture_move(self, move):
        return move.captured_piece is not None

    def generate_capture_moves(self):
        capture_moves = []
        all_moves = self.generate_legal_moves()
        for move in all_moves:
            if self.is_capture_move(move):
                capture_moves.append(move)
        return capture_moves

    def get_piece_value(self, piece):
        piece_values = {
            'P': 100, 'N': 320, 'B': 330, 'R': 500, 'Q': 900, 'K': 20000,
            'p': 100, 'n': 320, 'b': 330, 'r': 500, 'q': 900, 'k': 20000
        }
        return piece_values.get(piece, 0)

    def update_zobrist_hash(self, move, undo=False):
        piece = move.piece
        from_square = move.from_square
        to_square = move.to_square
        captured_piece = move.captured_piece

        if not undo:
            self.zobrist_hash ^= self.zobrist_piece_keys[piece][from_square]
            self.zobrist_hash ^= self.zobrist_piece_keys[piece][to_square]
            if captured_piece:
                self.zobrist_hash ^= self.zobrist_piece_keys[captured_piece][to_square]
        else:
            if captured_piece:
                self.zobrist_hash ^= self.zobrist_piece_keys[captured_piece][to_square]
            self.zobrist_hash ^= self.zobrist_piece_keys[piece][to_square]
            self.zobrist_hash ^= self.zobrist_piece_keys[piece][from_square]

    def generate_fen(self):
        fen = ""
        for rank in range(7, -1, -1):
            empty = 0
            for file in range(8):
                square = rank * 8 + file
                piece = self.get_piece_at_square(square)
                if piece:
                    if empty > 0:
                        fen += str(empty)
                        empty = 0
                    fen += piece
                else:
                    empty += 1
            if empty > 0:
                fen += str(empty)
            if rank != 0:
                fen += '/'
        fen += ' ' + ('w' if self.white_to_move else 'b')
        castling = ''
        for c in ['K', 'Q', 'k', 'q']:
            if self.castling_rights.get(c, False):
                castling += c
        fen += ' ' + (castling if castling else '-')
        fen += ' ' + (square_to_algebraic(self.en_passant_target) if self.en_passant_target is not None else '-')
        fen += f' {self.halfmove_clock}'
        fen += f' {self.fullmove_number}'

        print(f"Generated FEN: {fen}")
        return fen

    def uci_to_move(self, uci_move):
        """
        Converts a UCI move string to a Move object.
        """
        from_sq = algebraic_to_square(uci_move[:2])
        to_sq = algebraic_to_square(uci_move[2:4])
        promoted_piece = uci_move[4] if len(uci_move) > 4 else None
        piece = self.get_piece_at_square(from_sq)
        captured_piece = self.get_piece_at_square(to_sq)
        is_castling = False
        is_en_passant = False

        if piece.upper() == 'K' and abs(to_sq - from_sq) == 2:
            is_castling = True

        if piece.upper() == 'P' and to_sq == self.en_passant_target:
            is_en_passant = True
            captured_piece = 'p' if self.white_to_move else 'P'

        move = Move(
            piece=piece,
            from_square=from_sq,
            to_square=to_sq,
            captured_piece=captured_piece,
            promoted_piece=promoted_piece.upper() if promoted_piece else None,
            is_en_passant=is_en_passant,
            is_castling=is_castling
        )
        return move

    def suggest_move(self):
        """
        Uses both MovePredictor and Minimax to suggest the best move.
        The AI first attempts to use the MovePredictor. If the predicted move
        is invalid or suboptimal, it falls back to using Minimax.
        Returns:
            Move or None: The best move found.
        """
        fen = self.generate_fen()
        legal_moves = self.generate_legal_moves()

        predicted_move_str = self.move_predictor.predict_move(fen, legal_moves)
        if predicted_move_str:
            move = self.uci_to_move(predicted_move_str)
            if move and move in legal_moves:
                print(f"MovePredictor suggests: {move}")
                return move
            else:
                print(f"MovePredictor suggests: {predicted_move_str} (Invalid Move)")

        print("MovePredictor did not suggest a valid move. Falling back to Minimax.")
        best_move = find_best_move(self, max_depth=9, time_limit=5.0)
        if best_move:
            print(f"Minimax selects: {best_move}")
            return best_move
        else:
            print("Minimax found no legal moves.")
            return None

    def evaluate_board(self):
        return evaluate(self)

class Move:
    def __init__(
        self,
        piece,
        from_square,
        to_square,
        captured_piece=None,
        promoted_piece=None,
        is_en_passant=False,
        is_castling=False,
    ):
        self.piece = piece
        self.from_square = from_square
        self.to_square = to_square
        self.captured_piece = captured_piece
        self.promoted_piece = promoted_piece
        self.is_en_passant = is_en_passant
        self.is_castling = is_castling
        self.is_check = False

    def __eq__(self, other):
        return (
            isinstance(other, Move) and
            self.piece == other.piece and
            self.from_square == other.from_square and
            self.to_square == other.to_square and
            self.captured_piece == other.captured_piece and
            self.promoted_piece == other.promoted_piece and
            self.is_en_passant == other.is_en_passant and
            self.is_castling == other.is_castling
        )

    def __hash__(self):
        return hash((
            self.piece,
            self.from_square,
            self.to_square,
            self.promoted_piece,
            self.is_en_passant,
            self.is_castling,
        ))

    def __repr__(self):
        move_str = f"{square_to_algebraic(self.from_square)}{square_to_algebraic(self.to_square)}"
        if self.promoted_piece:
            move_str += f"={self.promoted_piece}"
        if self.is_castling:
            if self.to_square in [6, 62]:
                move_str = "O-O"
            elif self.to_square in [2, 58]:
                move_str = "O-O-O"
        return move_str
