import chess
import os.path

folders_to_check = []
current_node = None
next_node = None
new_node_count = 0
expected_equalities = 0

def add_folder(pathToParentNode, nodeID):
    global folders_to_check
    folders_to_check.append(os.path.join(pathToParentNode, str(nodeID)))


def filename(pathToNode):
    return os.path.join(pathToNode, "info")


def is_tablebase(char):
    return char in ("?", "w", "d", "l")

# tablebase
def check_first(filename, line):
    assert is_tablebase(line), f"1st@{filename} was {line}"


# draw reason
def check_second(filename, line):
    assert line in ("?", "dead position"), f"2nd@{filename} was {line}"


# id
def check_third(filename, line):
    global current_node
    assert line == f"#{current_node}", f"3rd@{filename} was {line}, expected #{current_node}"


def check_fourth(folder, filename, line):
    global folders_to_check
    global new_node_count
    global next_node
    if line == "":
        return

    start = str(next_node)
    assert line.startswith(start), f"4th@{filename} was {line}, expected to start with {start}"

    # Actually the last_child + 1
    # Default if line == start
    last_child = next_node + 1

    if line != start:
        start = start + ".."
        assert line.startswith(start), f"4th@{filename} was {line}, expected to start with {start}"

        line = line[len(start):]
        last_child = None
        try:
            last_child = int(line) + 1
        except ValueError:
            assert False, f"4th@{filename} did not end in an integer? End: {line}"

        assert last_child > next_node, f"4th@{filename} was {line}, unexpected range syntax because {last_child} <= {next_node}"

    for i in range(next_node, last_child):
        folders_to_check.append(os.path.join(folder, str(i)))
    new_node_count = last_child - next_node
    next_node = last_child


def check_fifth(filename, line):
    global expected_equalities
    global new_node_count

    assert len(line) >= new_node_count, f"5th@{filename}: Expected at least {new_node_count} chars but {line} is length {len(line)}"

    for char in line:
        assert is_tablebase(char), f"5th@{filename}: Unexpected character(s) in {line}: {[chara for chara in line if not is_tablebase(chara)]}"

    expected_equalities = len(line) - new_node_count


def check_rest(filename, lines):
    min_node = next_node - new_node_count
    equalities = 0
    for line in lines:
        if "≡" in line:
            equalities += 1
            parts = line.split("≡")
            assert len(parts) == 2, f"rest@{filename}: Two or more ≡ in the same line? ({line})"
            try:
                parts = [int(part) for part in parts]
            except ValueError:
                assert False, f"rest@{filename}: Non-integer in {line}"
            assert min_node <= parts[0] >= parts[1], f"rest@{filename}: Non-perfectly well ordered. Expected {min_node} <= {parts[0]} >= {parts[1]} at line {line}"
            min_node = parts[0]
        else:
            break

    assert equalities == expected_equalities, f"Based on the 4th and 5th lines, rest@{filename} should have {expected_equalities} equalities, but actually has {equalities}."

    try:
        board = chess.Board(line)
    except ValueError as err:
        print(err)
        assert False, f"Invalid fen syntax@{filename}: {line}"

    assert board.is_valid(), f"Invalid board with the fen@{filename}, {line}"


def check():
    global current_node
    global folders_to_check
    global new_node_count
    hole = []
    while folders_to_check:
        new_node_count = 0
        folder = folders_to_check.pop(0)
        if current_node % 77 == 0:
            print(current_node, folder)

        _filename = filename(folder)
        try:
            with open(_filename) as f:
                check_first(_filename, f.readline()[:-1])
                check_second(_filename, f.readline()[:-1])
                check_third(_filename, f.readline()[:-1])
                check_fourth(folder, _filename, f.readline()[:-1])
                check_fifth(_filename, f.readline()[:-1])
                check_rest(_filename, [line[:-1] for line in f.readlines()])
            if hole:
                print(f"Missing: {hole}")
        except FileNotFoundError:
            hole.append(current_node)

        current_node += 1


def check_cache():
    import pickle
    try:
        with open('cache.pickle', 'rb') as f:
            currentlayer, nextlayer, nextID, boardata = pickle.load(f)
            assert nextID == next_node
        print("cache OK")
    except FileNotFoundError:
        print("No cache found, skipped")


def init():
    global current_node
    global next_node
    add_folder("./", 0)
    current_node = 0
    next_node = 1


def main():
    init()
    check()
    check_cache()
    print("PASS")
    print(f"Nodes: {current_node}")


if __name__ == "__main__":
    main()
