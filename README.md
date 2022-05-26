# chesstree

The tree of chess

## reading

In order to completely describe a board position, you need to describe:

1. Current board state + Half move
2. Previous board states

Each board state has:

1. Board
2. Side to move
3. Castling
4. En passant, but only if the opponent can do En passant next move.

The previous board states are needed to check for repetition, which the file structure tree naturally fits.

## grammar

Here, the FEN is really a board state.
So the move count is excluded, en passant only exists if it's possible, etc.

Technically, with the "from" lines, the FEN is redundant, since you have the list of moves already.
Maybe I should remove them

And the grammar is:

```rust
/tablebase
/draw reason
#Id
/range
zero or more /tablebase not separated by newlines
zero or more /equivalent separated by newlines
FEN
```

### `/tablebase`

```js
// Information about theoretically perfect play:
? // Unknown
= // Draw
> // side to move wins
< // side to move loses
```

### `/draw reason`

```txt
dead position
insufficient material
stalemate
threefold repetition
fifty moves
?
```

### `/range`

```rust
// Empty line
Id // Single child
Id..Id // Two or more children
```

### `/equivalent`

```rust
Id≡Id

// Two nodes can have different move orders but otherwise be equivalent
// The "only" information that matters for a position is:
set of moves since last 50 move counter reset
where the pieces are on the board
en passant
castling

// For example, two equivalent positions are:
// a4 a5 b4
// b4 a5 a4
```

## file structure

Files are organized from top node to bottom node. (Really an upside-down tree)
The top node is the starting position.

Each node is represented by a folder.
Each folder has "info.txt" and then child nodes/folders.
This way, you don't have to worry about folder limits.

The moves are ordered by (8-1), (a-h), (piece from, piece to, alphabetical promotion)
The first instance of a node stays. Duplicate nodes shouldn't exist

## wait a minute

_"Isn't this impossible?"_ Yes

Note: Maybe in a billion trillion years it would be possible, since
`Number of states of atom in the universe > total chess positions > number of atoms in the universe`

If this project gets over 1 GB, part 2 will be on a different repo. To be determined.
But `1 GB = 1 000 000 000 bytes = 1 billion characters`, (text is very efficient), so I don't expect to reach that point soon.
