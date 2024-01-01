from dataclasses import dataclass

@dataclass
class Player:
    side: str
    turn: bool = False
    in_check: bool = False
    had_castled: bool = False # to change to castling rights to identify if rook has moved.

    def __post_init__(self) -> None:
        av_sides = ["White", "Black"]
        if self.side not in av_sides:
            raise ValueError(f"Use one of the available sides: {av_sides}")
        
    def change_turn(self):
        self.turn = not self.turn
    
    def raise_check(self):
        self.in_check = True

    def clear_check(self):
        self.in_check = False
