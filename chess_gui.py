import tkinter as tk
from tkinter import messagebox
import chess
from PyChess import ai_move, find_opening_match, load_opening_fens, load_opening_fens_from_epd

class ChessGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Chess Game with AI")
        self.board = chess.Board()

        self.canvas = tk.Canvas(master, width=480, height=480)
        self.canvas.pack()
        self.draw_board()
        self.canvas.bind("<Button-1>", self.click)
        self.selected_square = None
        self.user_move = None
        self.opening_fens = load_opening_fens(r"C:\Users\firefly\Documents\chessOp\TwoMoves_v1.pgn") + \
                    load_opening_fens_from_epd(r"C:\Users\firefly\Documents\chessOp\dFRC_openings.epd") + \
                    load_opening_fens_from_epd(r"C:\Users\firefly\Documents\chessOp\popularpos_lichess.epd")

        self.update_board()

    def draw_board(self):
        colors = ['#F0D9B5', '#B58863']
        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % 2]
                x0 = col * 60
                y0 = row * 60
                x1 = x0 + 60
                y1 = y0 + 60
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="black")

    def update_board(self):
        self.canvas.delete("piece")

        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece is not None:
                self.draw_piece(piece, square)

    def draw_piece(self, piece, square):
        piece_symbol = piece.symbol()
        col, row = chess.square_file(square), chess.square_rank(square)

        x0 = col * 60 + 30
        y0 = (7 - row) * 60 + 30

        self.canvas.create_text(x0, y0, text=piece_symbol, font=("Helvetica", 32), tags="piece")

    def click(self, event):
        col = event.x // 60
        row = 7 - (event.y // 60)
        clicked_square = chess.square(col, row)

        if self.selected_square is None:
            piece = self.board.piece_at(clicked_square)
            if piece and piece.color == chess.WHITE:
                self.selected_square = clicked_square
        else:
            move = chess.Move(self.selected_square, clicked_square)
            if move in self.board.legal_moves:
                self.board.push(move)
                self.update_board()
                self.selected_square = None
                self.master.after(1000, self.ai_turn)
            else:
                messagebox.showerror("Invalid Move", "That move is not legal!")
                self.selected_square = None

    def ai_turn(self):
        if not self.board.is_game_over():
            match_opening = find_opening_match(self.board, self.opening_fens)
            if match_opening:
                self.board.set_fen(match_opening)
            else:
                ai_move_to_play = ai_move(self.board, depth=3)
                self.board.push(ai_move_to_play)
            self.update_board()

        if self.board.is_game_over():
            result = self.board.result()
            messagebox.showinfo("Game Over", f"Result: {result}")

if __name__ == "__main__":
    root = tk.Tk()
    gui = ChessGUI(root)
    root.mainloop()
