import os
from typing import Optional

import chess

Version = int | str
Id = int
Path = str
Node = tuple[Path, tuple[chess.Move], Id]
Layer = list[Node]
MoveTuple = tuple[int, int, int]
BoardTuple = tuple[int, int, int, int, int, int, int, bool, int, chess.Square]
Equiv = tuple[BoardTuple, tuple[BoardTuple], int]

version: Version = 1
currentlayer: Layer = [("./", (), 0)]
nextlayer: Layer = []
nextID: int = 1
boardata: dict[Equiv, tuple[Path, Id]] = {}

def move_to_tuple(move: chess.Move) -> MoveTuple:
    return (move.from_square, move.to_square, move.promotion)


def board_to_tuple(board: chess.Board) -> BoardTuple:
    return (
        board.pawns, board.knights, board.bishops, board.rooks,
        board.queens, board.kings, board.occupied_co[chess.WHITE],
        board.turn, board.castling_rights, board.ep_square if board.has_legal_en_passant() else -1)

# Returns a sorted tuple of moves since the last irreversible move
# and the number of positions that add to the 100 ply counter but aren't actually reachable
def _equiv_movedata(board: chess.Board) -> tuple[tuple[BoardTuple], int]:
    # Actually a list of reachable positions, previous moves don't matter
    move_stack: list[chess.Board] = []
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
            move_stack.append(board_to_tuple(board2.copy()))
        board2.push(move)

    move_stack.sort()
    return (tuple(move_stack), irreversible_non_zeroing)


# Returns only the necessary data needed to see if two positions are equivalent
def to_equiv(board: chess.Board) -> Equiv:
    move_stack, irreversible_non_zeroing = _equiv_movedata(board)
    return (board_to_tuple(board), move_stack, irreversible_non_zeroing)


# Symmetries
def none(bt: BoardTuple) -> BoardTuple:
    return bt


def vmirr(bt: BoardTuple) -> BoardTuple:
    return (
        chess.flip_vertical(bt[0]),
        chess.flip_vertical(bt[1]),
        chess.flip_vertical(bt[2]),
        chess.flip_vertical(bt[3]),
        chess.flip_vertical(bt[4]),
        chess.flip_vertical(bt[5]),
        chess.flip_vertical(bt[6]),
        bt[7],
        chess.flip_vertical(bt[8]),
        -1 if bt[9] == -1 else bt[9] ^ 0b111000,
    )


def hmirr(bt: BoardTuple) -> BoardTuple:
    return (
        chess.flip_horizontal(bt[0]),
        chess.flip_horizontal(bt[1]),
        chess.flip_horizontal(bt[2]),
        chess.flip_horizontal(bt[3]),
        chess.flip_horizontal(bt[4]),
        chess.flip_horizontal(bt[5]),
        chess.flip_horizontal(bt[6]),
        bt[7],
        chess.flip_horizontal(bt[8]),
        -1 if bt[9] == -1 else bt[9] ^ 0b000111,
    )


def dmirr(bt: BoardTuple) -> BoardTuple:
    return (
        chess.flip_diagonal(bt[0]),
        chess.flip_diagonal(bt[1]),
        chess.flip_diagonal(bt[2]),
        chess.flip_diagonal(bt[3]),
        chess.flip_diagonal(bt[4]),
        chess.flip_diagonal(bt[5]),
        chess.flip_diagonal(bt[6]),
        bt[7],
        chess.flip_diagonal(bt[8]),
        -1 if bt[9] == -1 else chess.square_file(bt[9]) << 3 + chess.square_rank(bt[9]),
    )


def d2mirr(bt: BoardTuple) -> BoardTuple:
    return hmirr(dmirr(bt))


def rot180(bt: BoardTuple) -> BoardTuple:
    return hmirr(vmirr(bt))


def rotc(bt: BoardTuple) -> BoardTuple:
    return vmirr(dmirr(bt))


def rotcc(bt: BoardTuple) -> BoardTuple:
    return d2mirr(hmirr(bt))


def switch_sides(bt: BoardTuple) -> BoardTuple:
    return (
        bt[0],
        bt[1],
        bt[2],
        bt[3],
        bt[4],
        bt[5],
        bt[6],
        (bt[0] | bt[1] | bt[2] | bt[3] | bt[4] | bt[5] | bt[6]) ^ bt[7],
        0, # Castling is ruined
        bt[9]
    )


def transform_equiv(equiv: Equiv, transform, switch) -> Equiv:
    if switch:
        return (
            transform(switch_sides(equiv[0])),
            (transform(switch_sides(e)) for e in equiv[1]),
            equiv[2]
        )
    else:
        return (
            switch_sides(equiv[0]),
            (switch_sides(e) for e in equiv[1]),
            equiv[2]
        )



def has_equiv(equiv: Equiv) -> Optional[tuple[Path, Id]]:
    if equiv in boardata:
        return boardata[equiv]

    # No symmetries if castling*
    pawns = False
    boardtuples = (equiv[0],) + equiv[1]
    for boardtuple in boardtuples:
        if boardtuple[0] != 0:
            pawns = True
        elif boardtuple[7] != 0:
            return None

    rotated = transform_equiv(equiv, rot180, True)
    if rotated in boardata:
        return boardata[rotated]

    vmirrored = transform_equiv(equiv, vmirr, True)
    if vmirrored in boardata:
        return boardata[vmirrored]

    hmirrored = transform_equiv(equiv, hmirr, False)
    if hmirrored in boardata:
        return boardata[hmirrored]

    if pawns:
        return None

    switched = transform_equiv(equiv, none, True)
    if switched in boardata:
        return boardata[switched]

    rotated2 = transform_equiv(equiv, rot180, False)
    if rotated2 in boardata:
        return boardata[rotated2]

    vmirrored2 = transform_equiv(equiv, vmirr, False)
    if vmirrored2 in boardata:
        return boardata[vmirrored2]

    hmirrored2 = transform_equiv(equiv, hmirr, True)
    if hmirrored2 in boardata:
        return boardata[hmirrored2]

    clockroted = transform_equiv(equiv, rotc, False)
    if clockroted in boardata:
        return boardata[clockroted]
    cclocroted = transform_equiv(equiv, rotcc, False)
    if cclocroted in boardata:
        return boardata[cclocroted]
    dmirrored = transform_equiv(equiv, dmirr, False)
    if dmirrored in boardata:
        return boardata[dmirrored]
    d2mirrored = transform_equiv(equiv, d2mirr, False)
    if d2mirrored in boardata:
        return boardata[d2mirrored]
    clockroted2 = transform_equiv(equiv, rotc, True)
    if clockroted2 in boardata:
        return boardata[clockroted2]
    cclocroted2 = transform_equiv(equiv, rotcc, True)
    if cclocroted2 in boardata:
        return boardata[cclocroted2]
    dmirrored2 = transform_equiv(equiv, dmirr, True)
    if dmirrored2 in boardata:
        return boardata[dmirrored2]
    d2mirrored2 = transform_equiv(equiv, d2mirr, True)
    if d2mirrored2 in boardata:
        return boardata[d2mirrored2]
    return None




def sorted_legal_moves(board: chess.Board) -> list[chess.Move]:
    return sorted(board.legal_moves, key=move_to_tuple)


# This function is getting too big
def make_node_and_update(root: int, nextID: int, path: str, stack: tuple[chess.Move, ...]):
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
        is_equiv = has_equiv(equiv)
        if is_equiv:
            # actual data
            actual_path, actual_index = is_equiv

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
            moveresults += "l"
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


def update_from_layer_item(path: str, stack: tuple[chess.Move], nodeID: int):
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
    import shutil
    global currentlayer
    global nextlayer
    global nextID
    global boardata
    global version
    try:
        d = None
        with open('cache.pickle', 'rb') as f:
            d = pickle.load(f)

        v, c, nextl, nextI, b = d
        if v != version:
            print("Cache from outdated code, deleting cache")
            os.remove("cache.pickle")
            print("Deleting nodes")
            shutil.rmtree("0/")
            print("Regenerating nodes")
            for _ in range(nextI):
                make_next_node()
        else:
            currentlayer = c
            nextlayer = nextl
            nextID = nextI
            boardata = b

    except FileNotFoundError:
        print("No cache found, starting from scratch")

def store_cache():
    import pickle
    global currentlayer
    global nextlayer
    global nextID
    global boardata
    with open('cache.pickle', 'wb') as f:
        pickle.dump((version, currentlayer, nextlayer, nextID, boardata), f)


def main():
    load_cache()
    for _ in range(17017):
        make_next_node()
    store_cache()


if __name__ == "__main__":
    main()
