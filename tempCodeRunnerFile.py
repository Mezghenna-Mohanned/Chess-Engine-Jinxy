    if move_str in ['O-O', 'O-O-O']:
            # Castling moves
            if move_str == 'O-O':
                if self.board.white_to_move:
                    from_square = 4
                    to_square = 6
                else:
                    from_square = 60
                    to_square = 62
            else:
                if self.board.white_to_move:
                    from_square = 4
                    to_square = 2
                else:
                    from_square = 60
                    to_square = 58
            is_castling = True
            promoted_piece = None
        else:
            from_square = algebraic_to_square(move_str[0:2])
            to_square = algebraic_to_square(move_str[2:4])
            promoted_piece_char = move_str[4] if len(move_str) == 5 else None
            is_castling = False

        if from_square is None or to_square is None:
            return None

        piece = self.board.get_piece_at_square(from_square)
        if piece is None:
            return None

        captured_piece = self.board.get_piece_at_square(to_square) if self.board.is_square_occupied_by_opponent(to_square) else None

        is_en_passant = False
        if piece.upper() == 'P' and to_square == self.board.en_passant_target:
            is_en_passant = True

        promoted_piece = None
        if promoted_piece_char:
            if piece.isupper():
                # White pawn promoting
                promoted_piece = promoted_piece_char.upper()
            else:
                # Black pawn promoting
                promoted_piece = promoted_piece_char.lower()

        move = Move(
            piece=piece,
            from_square=from_square,
            to_square=to_square,
            captured_piece=captured_piece,
            promoted_piece=promoted_piece,
            is_en_passant=is_en_passant,
            is_castling=is_castling
        )

        return move
