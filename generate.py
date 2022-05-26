import os
from typing import List, Tuple

import chess

currentlayer = [("./", (), 0)]
nextlayer = []
nextID = 1
boardata = {}

def move_to_tuple(move: chess.Move):
    return (move.from_square, move.to_square, move.promotion)


# Returns a sorted tuple of moves since the last irrevers8ble move
# and the number of positions that add to the 100 ply counter but aren't actually reachable
def _equiv_movedata(board: chess.Board):
    move_stack = []
    irreversible_non_zeroing = 0
    board2 = chess.Board()
    for move in board.move_stack:
        if board2.is_zeroing(move):
            move_stack = []
            irreversible_non_zeroing = 0
        elif board2.is_irreversible(move):
            irreversible_non_zeroing += 1 + len(move_stack)
            move_stack = []
        else:
            move_stack.append(move)
        board2.push(move)

    move_stack = tuple(sorted(board.move_stack, key=move_to_tuple))
    return (move_stack, irreversible_non_zeroing)



# Returns only the necessary data needed to see if two positions are equivalent
def to_equiv(board: chess.Board):
    move_stack, irreversible_non_zeroing = _equiv_movedata(board)
    return (
        board.pawns, board.knights, board.bishops, board.rooks, board.queens, board.kings,
        board.castling_rights,
        None if not board.has_legal_en_passant() else board.ep_square,
        move_stack, irreversible_non_zeroing)


def sorted_legal_moves(board: chess.Board) -> List[chess.Move]:
    return sorted(board.legal_moves, key=move_to_tuple)


# This function is getting too big
def make_node_and_update(root: int, nextID: int, path: str, stack: Tuple[chess.Move, ...]):
    global boardata
    global nextlayer

    board = chess.Board()
    for move in stack:
        board.push(move)

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

        # ignore
        # actual_index = index (unused)
        actual_path = os.path.join(root_path, str(index))

        # check if equivalent
        equiv = to_equiv(board)
        is_equiv = equiv in boardata
        if is_equiv:
            # actual data
            actual_path, actual_index = boardata[equiv]

            # update equivs
            equivs += f"\n{index}≡{actual_index}"

            # don't `continue` since move info collection
            # is still necessary
        else:
            boardata[equiv] = (actual_path, index)

            # add to the next layer only if not equivalent
            stack2 = stack + (move,)
            nextlayer.append((root_path, stack2, index))

        # add moveresults + reasons
        outcome = board.outcome(claim_draw=True)

        # Since this is regular chess,
        # no need to check for is_variant_win() is_variant_draw() etc
        if board.is_checkmate():
            moveresults += "w"
        elif board.is_fifty_moves():
            moveresults += "d"
            reasons.add("fifty moves")
        elif board.is_stalemate():
            moveresults += "d"
            reasons.add("stalemate")
        elif board.is_insufficient_material():
            moveresults += "d"
            reasons.add("insufficient material")
        elif board.is_repetition():
            moveresults += "d"
            reasons.add("threefold repetition")
        else:
            # assert not board.is_game_over(), f"Game over?? {actual_path} {board.fen()}"

            try:
                with open(actual_path) as f:
                    moveresults += f.readline()
                    mr = f.readline()
                    if mr != "?":
                        reasons.add(mr)
            except OSError:
                moveresults += "?"

        board.pop()

        # Unsatisfying bug fix
        if not is_equiv:
            index += 1

    if "w" in moveresults:
        result = "l"
    elif "d" in moveresults:
        result = "d"
        if len(reasons) == 1:
            reason = reasons.pop()
        else:
            reason = "dead position"
    elif "l" in moveresults:
        result = "w"
    elif not moveresults:
        if board.is_checkmate():
            result = "l"
        else:
            result = "d"
            reason = "stalemate"

    if result == None:
        result = "?"
    if reason == None:
        reason = "?"

    range_ = ""
    if index - 1 == nextID:
        range_ = nextID
    elif index - 1 > nextID:
        range_ = f"{nextID}..{index - 1}"

    # When adding to `equivs`, there's always a newline at the start
    txt = f"{result}\n{reason}\n#{root}\n{range_}\n{moveresults}{equivs}\n{board.fen()}\n"

    try:
        os.makedirs(os.path.join(path, str(root)))
    except FileExistsError:
        pass
    with open(os.path.join(path, str(root), "info"), "w+") as f:
        # It's possible that not all bytes are written
        loops = 0
        while txt:
            txt = txt[f.write(txt):]
            loops += 1
            if loops > 10000:
                raise Exception("Could not write all info!", root, txt)
        f.flush()
        os.fsync(f.fileno())
    return index


def update_from_layer_item(path: str, stack: Tuple[chess.Move], nodeID: int):
    global nextID
    nextID = make_node_and_update(nodeID, nextID, path, stack)
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
        print("No cache found, starting from scratch")

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
