from app.board import Board
from app.player import Player
from app.projection_engine import Projection, CastlingRights

from icecream import ic

class GameState:
    def __init__(self, board=None):
        self.board = Board(board) if board else Board('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR')
        self.players = (Player("White",True),Player("Black"))
        self.turn = "White" if self.players[0].turn else "Black"
        self.white_to_move = True if self.players[0].turn else False
        self.move_log = []
        self.white_king_pos = (7,4)
        self.black_king_pos = (0,4)
        self.en_passant_possible = ()
        self.en_passant_log = []
        self.curr_castling_rights = CastlingRights()
        self.castling_rights_log = [CastlingRights()]
        self.in_check = False


    def change_turn(self):
        # Several redundant ways of selecting which player's turn. white_to_move is the most used one.
        # Other ways are left here in memory in case we need it later.
        for p in self.players:
            p.turn = not p.turn
        self.turn = "White" if self.players[0].turn else "Black"
        self.white_to_move = not self.white_to_move   

    def get_valid_moves(self):
        return Projection(self, self.board).get_valid_moves()

    def make_move(self, move):
        projected_board = Projection(self, self.board)
        ic(type(projected_board))
        ic(type(projected_board.board))
        ic(projected_board[1][0])
        ic(type(Board(projected_board.board)))
        ####################### CONTINUE HERE

        projected_board.make_projection(move)
        self.board = Board(projected_board.board)
        self.move_log.append(projected_board.projection_log[-1])
        self.change_turn()

    def undo_move(self):
        projected_board = Projection(self, self.board)
        projected_board.projection_log = self.move_log
        projected_board.undo_projection()
        self.board = Board(projected_board.board)

        self.change_turn()

    def update_board(self, board):
        self.board = Board(board)