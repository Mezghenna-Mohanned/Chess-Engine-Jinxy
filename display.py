def display_board(board):
    print("\n  +---+---+---+---+---+---+---+---+")
    for rank in range(7, -1, -1):
        print(f"{rank+1} |", end="")
        for file in range(8):
            square = rank * 8 + file
            piece = board.get_piece_at_square(square)
            print(f" {piece if piece else '.'} |", end="")
        print("\n  +---+---+---+---+---+---+---+---+")
    print("    a   b   c   d   e   f   g   h\n")
