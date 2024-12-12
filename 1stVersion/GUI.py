import json
import pygame
import sys
import os
from src.core.board import Board, Move, square_to_algebraic
from src.utils.utils import algebraic_to_square
import random
from src.Ai.minimax import find_best_move
from src.ml.predict_move import MovePredictor
from src.ml.rl_agent import RLAgent

pygame.init()

WIDTH, HEIGHT = 600, 600
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS
PIECE_SCALE = 0.6

WHITE_COLOR = (245, 245, 220)
BLACK_COLOR = (139, 69, 19)
TRANSPARENT_GREEN = (0, 255, 0, 100)
TRANSPARENT_BLUE = (0, 0, 255, 100)
TRANSPARENT_RED = (255, 0, 0, 150)

FONT = pygame.font.SysFont('Arial', 36)

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Chess AI')

def load_images():
    images = {}
    pieces = [
        'white_pawn-removebg-preview', 'white_knight-removebg-preview',
        'white_bishop-removebg-preview', 'white_rook-removebg-preview',
        'white_queen-removebg-preview', 'white_king-removebg-preview',
        'black_pawn-removebg-preview', 'black_knight-removebg-preview',
        'black_bishop-removebg-preview', 'black_rook-removebg-preview',
        'black_queen-removebg-preview', 'black_king-removebg-preview'
    ]
    for piece_name in pieces:
        filename = f"{piece_name}.png"
        filepath = os.path.join('images', filename)
        try:
            image = pygame.image.load(filepath)
            image = pygame.transform.scale(image, (int(SQUARE_SIZE * PIECE_SCALE), int(SQUARE_SIZE * PIECE_SCALE)))
            if 'white' in piece_name:
                color = 'w'
            else:
                color = 'b'
            piece_type = piece_name.split('_')[1]
            if 'pawn' in piece_type:
                key = 'P' if color == 'w' else 'p'
            elif 'knight' in piece_type:
                key = 'N' if color == 'w' else 'n'
            elif 'bishop' in piece_type:
                key = 'B' if color == 'w' else 'b'
            elif 'rook' in piece_type:
                key = 'R' if color == 'w' else 'r'
            elif 'queen' in piece_type:
                key = 'Q' if color == 'w' else 'q'
            elif 'king' in piece_type:
                key = 'K' if color == 'w' else 'k'
            if key:
                images[key] = image
        except pygame.error as e:
            print(f"Error loading image '{filepath}': {e}")
            sys.exit()
    return images

if not os.path.exists('images'):
    print("Images directory 'images/' not found. Please create it and add piece images.")
    sys.exit()

PIECE_IMAGES = load_images()

class GUI:
    def __init__(self, board: Board):
        self.board = board
        self.selected_square = None
        self.valid_moves = []
        self.running = True
        self.king_in_check = False
        self.king_square = None
        self.play_again_rect = None
        self.exit_rect = None
        self.promotion_move = None
        self.promotion_pieces = ['Q', 'R', 'B', 'N']
        self.promotion_rects = []
        self.ai_vs_ai = False
        self.rl_agent = RLAgent()

    def draw_board(self):
        for row in range(ROWS):
            for col in range(COLS):
                color = WHITE_COLOR if (row + col) % 2 == 0 else BLACK_COLOR
                pygame.draw.rect(SCREEN, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def draw_pieces(self):
        for square in range(64):
            piece = self.board.get_piece_at_square(square)
            if piece:
                row = 7 - (square // 8)
                col = square % 8
                piece_key = piece if piece.isupper() else piece.lower()
                piece_image = PIECE_IMAGES.get(piece_key)
                if piece_image:
                    img_rect = piece_image.get_rect(center=(col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2))
                    SCREEN.blit(piece_image, img_rect)

    def highlight_squares(self):
        if self.selected_square is not None:
            self.highlight_square(self.selected_square, TRANSPARENT_BLUE)
            for move_square in self.valid_moves:
                self.highlight_square(move_square, TRANSPARENT_GREEN)
        if self.king_in_check and self.king_square is not None:
            self.highlight_square(self.king_square, TRANSPARENT_RED)

    def highlight_square(self, square, color):
        row = 7 - (square // 8)
        col = square % 8
        rect = pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        s.fill(color)
        SCREEN.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE))

    def get_square_clicked(self, pos):
        x, y = pos
        col = x // SQUARE_SIZE
        row = 7 - (y // SQUARE_SIZE)
        if 0 <= col < 8 and 0 <= row < 8:
            return row * 8 + col
        return None

    def main_loop(self, engine):
        clock = pygame.time.Clock()
        while self.running:
            if not self.board.is_game_over():
                self.draw_board()
                self.highlight_squares()
                self.draw_pieces()

                self.king_in_check = self.board.is_in_check()
                if self.king_in_check:
                    self.king_square = self.board.find_king_square(self.board.white_to_move)
                else:
                    self.king_square = None

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                        pygame.quit()
                        sys.exit()

                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        pos = pygame.mouse.get_pos()
                        if self.promotion_move:
                            for i, rect in enumerate(self.promotion_rects):
                                if rect.collidepoint(pos):
                                    promoted_piece = self.promotion_pieces[i]
                                    self.promotion_move.promoted_piece = promoted_piece
                                    self.board.make_move(self.promotion_move)
                                    print(f"Promotion chosen: {promoted_piece}")
                                    self.promotion_move = None
                                    break
                        elif not self.ai_vs_ai and self.board.white_to_move:
                            # User input handling remains the same
                            square = self.get_square_clicked(pos)

                            if square is not None:
                                if self.selected_square is None:
                                    piece = self.board.get_piece_at_square(square)
                                    if piece and piece.isupper():
                                        self.selected_square = square
                                        self.valid_moves = [move.to_square for move in self.board.generate_legal_moves() if move.from_square == square]
                                        print(f"Selected square: {square_to_algebraic(square)} with piece {piece}")
                                else:
                                    if square == self.selected_square:
                                        print(f"Deselected square: {square_to_algebraic(square)}")
                                        self.selected_square = None
                                        self.valid_moves = []
                                    elif square in self.valid_moves:
                                        legal_moves = self.board.generate_legal_moves()
                                        move_found = False
                                        for legal_move in legal_moves:
                                            if legal_move.from_square == self.selected_square and legal_move.to_square == square:
                                                if legal_move.promoted_piece:
                                                    self.promotion_move = legal_move
                                                    print(f"Move requires promotion: {legal_move}")
                                                else:
                                                    self.board.make_move(legal_move)
                                                    print(f"Player moves: {legal_move}")
                                                move_found = True
                                                break
                                        if move_found:
                                            self.selected_square = None
                                            self.valid_moves = []
                                        else:
                                            print("Invalid move attempted.")
                                            self.selected_square = None
                                            self.valid_moves = []
                                    else:
                                        piece = self.board.get_piece_at_square(square)
                                        if piece and piece.isupper():
                                            self.selected_square = square
                                            self.valid_moves = [move.to_square for move in self.board.generate_legal_moves() if move.from_square == square]
                                            print(f"Changed selection to square: {square_to_algebraic(square)} with piece {piece}")
                                        else:
                                            print(f"Clicked on invalid square: {square_to_algebraic(square)}")
                        else:
                            # In AI vs AI mode, no user input is needed
                            pass

                # AI vs AI mode
                if self.ai_vs_ai and self.running:
                    if not self.board.is_game_over():
                        legal_moves = self.board.generate_legal_moves()
                        if legal_moves:
                            action = self.rl_agent.select_action(self.board, legal_moves)
                            self.board.make_move(action)
                            # Update display after each move
                            self.draw_board()
                            self.draw_pieces()
                            pygame.display.flip()
                            pygame.event.pump()  # Process event queue
                            clock.tick(2)  # Adjust the speed as needed
                        else:
                            print("No legal moves available.")
                    else:
                        print("Game over.")
                        self.running = False

                # If not AI vs AI mode and it's AI's turn
                elif not self.board.white_to_move and not self.ai_vs_ai:
                    ai_move = engine.get_ai_move(self.board)
                    if ai_move:
                        print(f"AI suggests: {ai_move}")
                        move_obj = self.parse_move(ai_move)
                        if move_obj and move_obj in self.board.generate_legal_moves():
                            self.board.make_move(move_obj)
                            print(f"AI plays: {ai_move}")
                            print(f"AI moved: {move_obj}")
                        else:
                            print("AI selected an invalid move. Selecting a legal move using Minimax.")
                            best_move = find_best_move(self.board, max_depth=9, time_limit=5.0)  # Increased depth for better analysis
                            if best_move:
                                self.board.make_move(best_move)
                                print(f"Minimax selects: {best_move}")
                            else:
                                print("Minimax found no legal moves.")
                    else:
                        print("AI has no legal moves.")

                pygame.display.flip()
                clock.tick(60)
            else:
                self.draw_board()
                self.draw_pieces()
                self.display_game_over()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        pos = pygame.mouse.get_pos()
                        if self.play_again_rect.collidepoint(pos):
                            print("Restarting game.")
                            self.restart_game()
                        elif self.exit_rect.collidepoint(pos):
                            print("Exiting game.")
                            self.running = False
                            pygame.quit()
                            sys.exit()

                pygame.display.flip()
                clock.tick(60)

    def display_game_over(self):
        """
        Displays the game over screen with options to play again or exit.
        """
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        SCREEN.blit(overlay, (0, 0))

        if self.board.is_checkmate():
            if self.board.white_to_move:
                message = "Black wins!"
            else:
                message = "White wins!"
        else:
            message = "Draw."

        text = FONT.render(message, True, (255, 255, 255))
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        SCREEN.blit(text, text_rect)

        play_again_text = FONT.render("Play Again", True, (255, 255, 255))
        play_again_rect = play_again_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
        pygame.draw.rect(SCREEN, (0, 128, 0), play_again_rect.inflate(20, 10))
        SCREEN.blit(play_again_text, play_again_rect)

        exit_text = FONT.render("Exit", True, (255, 255, 255))
        exit_rect = exit_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80))
        pygame.draw.rect(SCREEN, (128, 0, 0), exit_rect.inflate(20, 10))
        SCREEN.blit(exit_text, exit_rect)

        self.play_again_rect = play_again_rect
        self.exit_rect = exit_rect

        pygame.display.flip()

    def restart_game(self):
        """
        Restarts the game by reinitializing the board and resetting UI elements.
        """
        self.board = Board()
        self.selected_square = None
        self.valid_moves = []
        self.king_in_check = False
        self.king_square = None
        self.promotion_move = None
        self.promotion_rects = []
        print("Game has been restarted.")

    def draw_promotion_choices(self):
        """
        Displays the promotion choices when a pawn reaches the last rank.
        """
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        SCREEN.blit(overlay, (0, 0))

        text = FONT.render("Choose promotion piece:", True, (255, 255, 255))
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
        SCREEN.blit(text, text_rect)

        self.promotion_rects = []
        piece_size = SQUARE_SIZE
        y = HEIGHT // 2 - piece_size // 2
        x_start = WIDTH // 2 - 2 * piece_size + 30

        for i, piece_char in enumerate(self.promotion_pieces):
            piece = piece_char if self.board.white_to_move else piece_char.lower()
            image = PIECE_IMAGES.get(piece)
            if image:
                x = x_start + i * (piece_size + 20)
                rect = pygame.Rect(x, y, piece_size, piece_size)
                SCREEN.blit(image, rect)
                self.promotion_rects.append(rect)

    def parse_move(self, move_str):
        """
        Converts a UCI move string into a Move object.
        """
        promoted_piece_char = None

        if move_str in ['O-O', 'O-O-O']:
            if move_str == 'O-O':
                if not self.board.white_to_move:
                    from_square = 60  # Black King
                    to_square = 62
                else:
                    from_square = 4  # White King
                    to_square = 6
            else:
                if not self.board.white_to_move:
                    from_square = 60  # Black King
                    to_square = 58
                else:
                    from_square = 4  # White King
                    to_square = 2
            is_castling = True
            captured_piece = None
        else:
            from_square = algebraic_to_square(move_str[0:2])
            to_square = algebraic_to_square(move_str[2:4])
            promoted_piece_char = move_str[4] if len(move_str) == 5 else None
            is_castling = False
            captured_piece = self.board.get_piece_at_square(to_square) if self.board.is_square_occupied_by_opponent(to_square) else None

        if from_square is None or to_square is None:
            print(f"Invalid move string: {move_str}")
            return None

        piece = self.board.get_piece_at_square(from_square)
        if piece is None:
            print(f"No piece at from_square: {square_to_algebraic(from_square)}")
            return None

        is_en_passant = False
        if piece.upper() == 'P' and to_square == self.board.en_passant_target:
            is_en_passant = True
            captured_piece = 'p' if self.board.white_to_move else 'P'

        promoted_piece = None
        if promoted_piece_char:
            if piece.isupper():
                promoted_piece = promoted_piece_char.upper()
            else:
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

        print(f"Parsed move: {move}")
        return move

class ChessEngine:
    def __init__(self):
        self.move_predictor = MovePredictor()
        self.games_played = 0
        self.moves_learned = 0

    def learn_from_user_move(self, board, move):
        self.moves_learned += 1
        print(f"Learning from user move: {move}")
        self.move_predictor.update_model(board.to_fen(), move)
        print(f"Total moves learned: {self.moves_learned}")


    def get_ai_move(self, board: Board):
        self.games_played += 1
        print(f"\nAI thinking (Game {self.games_played})...")
        
        move = board.suggest_move()
        if move and move in board.generate_legal_moves():
            print(f"MovePredictor suggests: {move}")
            print(f"Confidence: {self.move_predictor.get_move_confidence(board.to_fen(), move):.2f}")
            return str(move)
        else:
            print("MovePredictor suggested an invalid move, falling back to Minimax.")
            best_move = find_best_move(board, max_depth=6, time_limit=5.0)
            if best_move:
                move_str = self.format_move(best_move)
                print(f"Minimax selects: {move_str}")
                return move_str
            else:
                print("Minimax found no legal moves.")
                return None


def main():
    # Uncomment the following lines to train the RL agent and watch AI vs AI gameplay

    #engine = ChessEngine()
    #board = Board()
    #gui = GUI(board)
    #gui.ai_vs_ai = True  #set to True for AI vs AI mode
    #gui.main_loop(engine)

    #for normal gameplay with human vs AI, keep the following lines

    engine = ChessEngine()
    board = Board()
    gui = GUI(board)
    gui.main_loop(engine)

if __name__ == "__main__":
    main()
