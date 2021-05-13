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

The previous board states are needed to check for repetition

## grammar
Here, the FEN is really a board state. So the move count is excluded, en passant (See above), etc.

And the grammar is:
```js
#Id
FEN

from [Id] by [move]
to [Id] by [move]
draw by ["dead position" | "stalemate" | "threefold repetition" | "fifty moves"]
checkmate
comment [any]
```

Files are organized from top node to bottom node. (Really an upside-down tree)  
The top node is the starting position.

Each node is represented by a folder.  
Each folder has "info.txt" and then child nodes/folders.  
This way, you don't have to worry about folder limits.

The moves are ordered by (a1-h8), (piece from, piece to, alphabetical promotion)  
The first instance of a node stays. Duplicate nodes shouldn't exist
