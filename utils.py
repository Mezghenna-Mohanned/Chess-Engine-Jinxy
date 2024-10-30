def algebraic_to_square(algebraic):
    files = {'a': 0, 'b': 1, 'c': 2, 'd': 3,
             'e': 4, 'f': 5, 'g': 6, 'h': 7}
    ranks = {'1': 0, '2': 1, '3': 2, '4': 3,
             '5': 4, '6': 5, '7': 6, '8': 7}

    if len(algebraic) != 2:
        return None
    file_char = algebraic[0]
    rank_char = algebraic[1]
    if file_char in files and rank_char in ranks:
        return ranks[rank_char] * 8 + files[file_char]
    else:
        return None

def square_to_algebraic(square):
    files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    rank = (square // 8) + 1
    file = square % 8
    if 0 <= file < 8 and 1 <= rank <= 8:
        return f"{files[file]}{rank}"
    else:
        return None
