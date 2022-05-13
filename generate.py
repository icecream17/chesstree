import chess
import os
from typing import List


currentlayer = [("./", (), 0)]
nextlayer = []
nextID = 1
boardata = {}

def move_to_tuple(move: chess.Move):
    return (move.from_square, move.to_square, move.promotion)


# Returns only the necessary data needed to see if two positions are equivalent
def to_equiv(board: chess.Board):
    return (
        board.pawns, board.knights, board.bishops, board.rooks, board.queens, board.kings,
        tuple(sorted(board.move_stack, key=move_to_tuple)),
        board.castling_rights,
        None if not board.has_legal_en_passant() else board.ep_square)


def sorted_legal_moves(board: chess.Board) -> List[chess.Move]:
    return sorted(board.legal_moves, key=move_to_tuple)


# This function is getting too big
def make_node_and_update(board: chess.Board, root: int, nextID: int, path: str, stack: tuple[chess.Move]):
    global boardata
    global nextlayer
    result = None
    reason = None
    moveresults = ""
    equivs = ""
    moves = sorted_legal_moves(board)
    reasons = set()
    index = nextID
    root_path = os.path.join(path, str(root))
    for move in moves:
        board.push(move)

        equiv = to_equiv(board)
        if equiv in boardata:
            equivs += f"\n{index}≡{boardata[equiv]}"
            board.pop()
            continue
        else:
            boardata[equiv] = index
        stack2 = stack + (move,)
        nextlayer.append((root_path, stack2, index))

        if board.is_variant_win():
            moveresults += "w"
        elif board.is_variant_draw():
            moveresults += "d"
            if board.is_fifty_moves():
                reasons.add("fifty moves")
            elif board.is_stalemate():
                reasons.add("stalemate")
            elif board.is_insufficient_material():
                reasons.add("insufficient material")
            elif board.is_repetition():
                reasons.add("threefold repetition")
            else:
                reasons.add("variant draw")
        elif board.is_variant_loss():
            moveresults += "l"
        else:
            try:
                with open(os.path.join(path, str(root), str(index))) as f:
                    moveresults += f.readline()
                    mr = f.readline()
                    if mr != "None":
                        reasons.add(mr)
            except OSError:
                moveresults += "?"
        board.pop()
        index += 1

    if "w" in moveresults:
        result = "w"
    elif "d" in moveresults:
        result = "d"
        if len(reasons) == 1:
            reason = reasons.pop()
        else:
            reason = "dead position"
    elif "l" in moveresults:
        result = "l"
    elif not moveresults:
        if board.is_checkmate():
            result = "l"
        else:
            result = "d"
            reason = "stalemate"

    txt = f"{result}\n{reason}\n#{root}\n{nextID}..{index - 1}\n{moveresults}\n{equivs}\n\n{board.fen()}\n"

    try:
        os.makedirs(os.path.join(path, str(root)))
    except FileExistsError:
        pass
    with open(os.path.join(path, str(root), "info"), "w+") as f:
        f.write(txt)
    return index


def update_from_layer_item(path: str, stack: tuple[chess.Move], nodeID: int):
    global nextID

    board = chess.Board()
    for move in stack:
        board.push(move)

    nextID = make_node_and_update(board, nodeID, nextID, path, stack)
    print(nodeID, nextID)


def make_next_node():
    global currentlayer
    global nextlayer
    if currentlayer:
        path, stack, nodeID = currentlayer.pop(0)
        update_from_layer_item(path, stack, nodeID)
    elif nextlayer:
        currentlayer = nextlayer
        nextlayer = []
        make_next_node()


def make_next_layer():
    global currentlayer
    global nextlayer
    # currentlayer: set of (str, tuple(), id)
    # nextlayer: set of (str, tuple(move), id)
    for (path, stack, nodeID) in currentlayer:
        update_from_layer_item(path, stack, nodeID)
    currentlayer = nextlayer
    nextlayer = []
    # print(currentlayer)

def load_cache():
    import pickle
    global currentlayer
    global nextlayer
    global nextID
    global boardata
    try:
        with open('cache.pickle', 'rb') as f:
            currentlayer, nextlayer, nextID, boardata = pickle.load(f)
    except FileNotFoundError:
        pass

def store_cache():
    import pickle
    global currentlayer
    global nextlayer
    global nextID
    global boardata
    with open('cache.pickle', 'wb') as f:
        pickle.dump((currentlayer, nextlayer, nextID, boardata), f)


def main():
    load_cache()
    for _ in range(77):
        make_next_node()
    store_cache()


if __name__ == "__main__":
    main()
