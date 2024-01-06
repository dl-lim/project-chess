from app.config import GAME_CONFIG
from app.fen import FENConverter

class Board:
    def __init__(self, board_input):
        if isinstance(board_input, str):
            self._init_from_fen_string(board_input)
        elif isinstance(board_input, Board):
            self._init_from_board_class(board_input)
        elif self._check_valid_board_list(board_input):
            self._init_from_board_list(board_input)
        else:
            raise TypeError('Use either a FEN string or a Board (list of lists)')

    def _init_from_fen_string(self, fen_string):
        self.fen = fen_string
        self.board = FENConverter.fen_to_board(self.fen)

    def _init_from_board_class(self, board_class):
        self.board = board_class.board
        self.fen = board_class.fen

    def _init_from_board_list(self, board_list):
        self.board = board_list
        self.fen = FENConverter.board_to_fen(self.board)

    def _check_valid_board_list(self, board):
        return (
        isinstance(board, list)
        and len(board) == GAME_CONFIG.DIMENSION
        and all(isinstance(inner_list, list) and len(inner_list) == GAME_CONFIG.DIMENSION for inner_list in board)
    )

    def __eq__(self, other):
        return self.fen == other.fen
    
    def __getitem__(self, index):
        return self.board[index]