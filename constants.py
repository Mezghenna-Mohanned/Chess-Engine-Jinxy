PIECE_VALUES = {
    'P': 100,  # White Pawn
    'N': 320,  # White Knight
    'B': 330,  # White Bishop
    'R': 500,  # White Rook
    'Q': 900,  # White Queen
    'K': 20000,  # White King
    'p': -100,  # Black Pawn
    'n': -320,  # Black Knight
    'b': -330,  # Black Bishop
    'r': -500,  # Black Rook
    'q': -900,  # Black Queen
    'k': -20000,  # Black King
}

INITIAL_POSITIONS = {
    'P': 0x000000000000FF00,
    'N': 0x0000000000000042,
    'B': 0x0000000000000024,
    'R': 0x0000000000000081,
    'Q': 0x0000000000000008,
    'K': 0x0000000000000010,
    'p': 0x00FF000000000000,
    'n': 0x4200000000000000,
    'b': 0x2400000000000000,
    'r': 0x8100000000000000,
    'q': 0x0800000000000000,
    'k': 0x1000000000000000,
}

POSITIONAL_VALUES = {

    'N': [
        -5, -4, -3, -3, -3, -3, -4, -5,
        -4, -2,  0,  0,  0,  0, -2, -4,
        -3,  0,  1,  1,  1,  1,  0, -3,
        -3,  0,  1,  2,  2,  1,  0, -3,
        -3,  0,  1,  2,  2,  1,  0, -3,
        -3,  0,  1,  1,  1,  1,  0, -3,
        -4, -2,  0,  0,  0,  0, -2, -4,
        -5, -4, -3, -3, -3, -3, -4, -5,
    ],
}

FILE_MASKS = [
    0x0101010101010101,  # File A
    0x0202020202020202,  # File B
    0x0404040404040404,  # File C
    0x0808080808080808,  # File D
    0x1010101010101010,  # File E
    0x2020202020202020,  # File F
    0x4040404040404040,  # File G
    0x8080808080808080,  # File H
]

FILE_A = FILE_MASKS[0]
FILE_B = FILE_MASKS[1]
FILE_C = FILE_MASKS[2]
FILE_D = FILE_MASKS[3]
FILE_E = FILE_MASKS[4]
FILE_F = FILE_MASKS[5]
FILE_G = FILE_MASKS[6]
FILE_H = FILE_MASKS[7]

RANK_MASKS = [
    0x00000000000000FF,  # Rank 1
    0x000000000000FF00,  # Rank 2
    0x0000000000FF0000,  # Rank 3
    0x00000000FF000000,  # Rank 4
    0x000000FF00000000,  # Rank 5
    0x0000FF0000000000,  # Rank 6
    0x00FF000000000000,  # Rank 7
    0xFF00000000000000,  # Rank 8
]

RANK_1 = RANK_MASKS[0]
RANK_2 = RANK_MASKS[1]
RANK_3 = RANK_MASKS[2]
RANK_4 = RANK_MASKS[3]
RANK_5 = RANK_MASKS[4]
RANK_6 = RANK_MASKS[5]
RANK_7 = RANK_MASKS[6]
RANK_8 = RANK_MASKS[7]

KNIGHT_MOVES = [0] * 64
KING_MOVES = [0] * 64

def initialize_move_masks():
    for square in range(64):
        rank = square // 8
        file = square % 8

        knight_offsets = [
            (2, 1), (1, 2), (-1, 2), (-2, 1),
            (-2, -1), (-1, -2), (1, -2), (2, -1)
        ]
        for dr, df in knight_offsets:
            r = rank + dr
            f = file + df
            if 0 <= r < 8 and 0 <= f < 8:
                KNIGHT_MOVES[square] |= 1 << (r * 8 + f)

        king_offsets = [
            (1, 0), (-1, 0), (0, 1), (0, -1),
            (1, 1), (1, -1), (-1, 1), (-1, -1)
        ]
        for dr, df in king_offsets:
            r = rank + dr
            f = file + df
            if 0 <= r < 8 and 0 <= f < 8:
                KING_MOVES[square] |= 1 << (r * 8 + f)

initialize_move_masks()

SLIDING_DIRECTIONS = {
    'bishop': [9, 7, -7, -9],
    'rook': [8, -8, 1, -1],
    'queen': [9, 7, -7, -9, 8, -8, 1, -1]
}

SQUARES = {square: {'neighbors': {}} for square in range(64)}

for square in range(64):
    rank = square // 8
    file = square % 8

    for piece_type, directions in SLIDING_DIRECTIONS.items():
        for direction in directions:
            neighbor_square = square + direction

            dr = direction // 8
            df = direction % 8

            if direction < 0:
                dr = (direction // 8)
                df = (direction % 8)

            new_rank = rank + (dr if dr < 0 else dr)
            new_file = file + (df if df < 0 else df)

            if 0 <= new_rank < 8 and 0 <= new_file < 8:
                SQUARES[square]['neighbors'][direction] = new_rank * 8 + new_file
            else:
                SQUARES[square]['neighbors'][direction] = None
