import chess

piece_values = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

def evaluate_material(board):
    """Evaluate the material balance on the board."""
    white_material = 0
    black_material = 0
    
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = piece_values[piece.piece_type]
            if piece.color == chess.WHITE:
                white_material += value
            else:
                black_material += value
                
    return white_material - black_material

def evaluate_king_safety(board):
    """Evaluate king safety, with castling bonuses."""
    white_king_safety = 0
    black_king_safety = 0
    
    if board.has_castling_rights(chess.WHITE):
        white_king_safety += 50
    if board.has_castling_rights(chess.BLACK):
        black_king_safety += 50
    
    return white_king_safety - black_king_safety

def evaluate_pawn_structure(board):
    """Evaluate pawn structure, with penalties for weaknesses like isolated or doubled pawns."""
    white_pawn_penalty = 0
    black_pawn_penalty = 0
    
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.piece_type == chess.PAWN:
            if piece.color == chess.WHITE:
                if board.is_pinned(chess.WHITE, square):
                    white_pawn_penalty += 10
            else:
                if board.is_pinned(chess.BLACK, square):
                    black_pawn_penalty += 10

    return black_pawn_penalty - white_pawn_penalty

def evaluate_piece_activity(board):
    """Evaluate piece activity and control of important squares like the center."""
    center_squares = [chess.D4, chess.E4, chess.D5, chess.E5]
    white_activity = 0
    black_activity = 0
    
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            if square in center_squares:
                if piece.color == chess.WHITE:
                    white_activity += 10
                else:
                    black_activity += 10
    
    return white_activity - black_activity

def evaluate_board_position(board):
    """Overall evaluation combining material, king safety, pawn structure, and piece activity."""
    material_score = evaluate_material(board)
    king_safety_score = evaluate_king_safety(board)
    pawn_structure_score = evaluate_pawn_structure(board)
    piece_activity_score = evaluate_piece_activity(board)
    
    total_score = material_score + king_safety_score + pawn_structure_score + piece_activity_score
    
    return total_score

def minimax(board, depth, maximizing_player):
    if depth == 0 or board.is_game_over():
        return evaluate_board_position(board)

    if maximizing_player:
        max_eval = float('-inf')
        for move in board.legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, False)
            board.pop()
            max_eval = max(max_eval, eval)
        return max_eval
    else:
        min_eval = float('inf')
        for move in board.legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, True)
            board.pop()
            min_eval = min(min_eval, eval)
        return min_eval
