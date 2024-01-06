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
        self.checkmate = False
        self.stalemate = False


    def change_turn(self):
        # Several redundant ways of selecting which player's turn. white_to_move is the most used one.
        # Other ways are left here in memory in case we need it later.
        for p in self.players:
            p.turn = not p.turn
        self.turn = "White" if self.players[0].turn else "Black"
        self.white_to_move = not self.white_to_move   

    def get_projection_at_current_state(self):
        return Projection(self, self.board)

    def get_valid_moves(self):
        return self.get_projection_at_current_state().get_valid_moves()

    def _update_attributes_from_projection(self, projection):
        self.board = Board(projection.board)
        self.white_king_pos = projection.white_king_pos
        self.black_king_pos = projection.black_king_pos
        self.en_passant_possible = projection.en_passant_possible
        self.curr_castling_rights = CastlingRights()
        self.in_check = projection.in_check
        self.checkmate = projection.checkmate
        self.stalemate = projection.stalemate

    def make_move(self, move):
        # Make projection
        projection = Projection(self, self.board)
        projection.make_projection(move)
        
        # Logging forward
        self.move_log.append(projection.projection_log[-1])
        self.en_passant_log.append(projection.en_passant_log[-1])
        self.castling_rights_log.append(projection.castling_rights_log)

        # Update other attributes and change turn
        self._update_attributes_from_projection(projection)
        self.change_turn()

    def undo_move(self):
        if len(self.move_log) > 0:
            # Make projection
            projection = Projection(self, self.board)
            projection.projection_log = self.move_log
            projection.undo_projection()

            # Logging backward
            self.move_log = projection.projection_log
            self.en_passant_log = projection.en_passant_log
            self.castling_rights_log = projection.castling_rights_log

            # Update other attributes and change turn
            self._update_attributes_from_projection(projection)
            self.change_turn()




    # def make_move(self, move):
    #     projected_board = Projection(self, self.board)
    #     projected_board.make_projection(move)
    #     self.board = Board(projected_board.board)
    #     self.move_log.append(projected_board.projection_log[-1])
    #     self.en_passant_log.append(projected_board.en_passant_log[-1])
    #     self.en_passant_possible = projected_board.en_passant_possible
    #     self.change_turn()

    # def undo_move(self):
    #     if len(self.move_log) > 0:
    #         projected_board = Projection(self, self.board)
    #         projected_board.projection_log = self.move_log
    #         projected_board.en_passant_log = self.en_passant_log
    #         self.en_passant_possible = projected_board.en_passant_possible
    #         projected_board.undo_projection()
    #         self.board = Board(projected_board.board)
    #         self.change_turn()

    def update_board(self, board):
        self.board = Board(board)