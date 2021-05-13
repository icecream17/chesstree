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
```js
#Id
FEN

from #Id
move) #Id
draw by ["dead position" | "stalemate" | "threefold repetition" | "fifty moves"]
checkmate!
comment [any]
```


move grammar:
```js
0. Empty! (this means only one is possible)
1. [row]
1. [column]
1. [piece]
2. [toSquare] // a: Only pawn, or b: Only piece
2. [piece][toFile]
2. [piece][toRank]
3. [piece][toSquare]
3. [fromFile][toSquare]
3. [fromRank][toSquare]
3. [toSquare][promotionPiece]
4. [fromFile][toSquare][promotionPiece]
4. [fromSquare][toSquare]

// Pieces are capitalized, squares are not
// The minimum length disambiguation possible is always used
// The list above is ordered by how many characters it uses

// h-pawn takes on g8, promoting to a bishop, checkmate
 // If this move was forced that would be amazing
g
8
P
g8
Pg
P8
Pg8 // Honestly this is just as good as hg8
hg8
7g8 // Silly - first representation that won't ever happen
g8B
hg8B
h7g8 // Note: In this case it doesn't disambiguate enough. So use [fromFile][toSquare][promotionPiece] instead
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
