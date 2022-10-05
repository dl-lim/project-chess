# Project Chess

This repo contains a fully playable chess game with move validation and all special moves like En Passant and Castling.

This is a project I will continually be working on to optimise and improve.

Unfortunately AI is still a WIP - I will be starting with a naive random AI, to a greedy AI and then implementing stockfish later on. 

More work needs to be done on the interface to include a move log, captured pieces, black/white switch and AI selector.

## Instructions
To start, run `main.py`

Pressing the `R` key during gameplay resets the board

Pressing the `Z` key during gameplay undo's a move


<details><summary>Notes for self</summary>

### Story
why use valid_moves[i] instead of move in valid_moves
move does not have Move class parameters

### Improvements:
consider passing team parameter through functions
</details>