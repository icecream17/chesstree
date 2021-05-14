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
/move/tablebase/ #Id
draw by /draw reason/
checkmate!
comment [any text]
```

`/draw reason/`:
```
dead position
insufficient material
stalemate
threefold repetition
fifty moves
```

`/move/` grammar:
```js
// Here, all of the fields surrounded by [square brackets like this] are optional
// Try to ***use the least amount of fields possible**!!!
move =
   [piece] [captureInfo] [fromToInfo] [promotionIndicator] [checkIndicator] [checkmateIndicator]
   [piece] [captureInfo] [fromToInfo] [promotionPiece] [checkIndicator] [checkmateIndicator]

captureInfo =
   captureIndicator [piece]

captureIndicator = "x"
promotionIndicator = "="
checkIndicator = "+"
checkmateIndicator = "#"

// You cannot have "fromRank" without "toRank" (so cc is possible, but not c1 or c by itself)
// You cannot have "fromFile" without "toFile" or "toRank" (so 1c and 12 are possible, but not 1 by itself)
fromToInfo =
   [fromRank] [fromFile] toRank [toFile]
   [fromFile] toFile

piece =
   PBNRQK
file =
   abcdefgh
rank =
   12345678

// Example:
// Consider (exc1=Q#). How is it represented in this optimized format?

// If the move is forced, the best representation is the empty string (!!!!)
// Else:
//  If there's only 1 pawn move
P
//  If there's only 1 move that captures
x
//  If there's only 1 move that goes to rank 1
1
// .....
//  If there's only 1 move that checks (redundant in this case)
+
//  If there's only 1 move that checkmates
#
//  If there's only 1 pawn move that captures
Px
// .....
// You get the idea. 


// Note that the longest representation is 4 characters
// Let's say there's queens at c3, c5 and e3
// Qc3e5
//   cannot beomce c3e since Qc3e1,
//   and not c35 since Qc1e5,
//   and not 3e5 or Q35, since Qe3e5,
//   and not ce5 or Qe5, since Qc5e5,
//   c3e5 is the minimum

// Longest promotion is 3 characters
fromFile toFile promotionPiece (e.g. with efB, disambiguates exf8=B from gxf8=B, exd8=B, exf8=N)
```

`/tablebase/`
```js
// Information about theoretically perfect play:
) // Unknown
= // Draw
> // side to move wins
< // side to move loses

// Examples:
Qxf7)
Qxf7=
Qxf7|w
Qxf7|b
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
