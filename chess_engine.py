import fen


class GameState:
    def __init__(self):
        self.board = fen.fen_to_board('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR')
        self.white_to_move = True
        self.move_log = []

    def make_move(self,Move):
        """
        Use Move object to make a move, does not work for castling and en passant
        """
        self.board[Move.start_row][Move.start_col] = '--'
        self.board[Move.end_row][Move.end_col] = Move.piece_moved
        self.move_log.append(Move)
        self.white_to_move = not self.white_to_move


    def undo_move(self):
        if len(self.move_log) > 0:
            previous_move = self.move_log.pop()
            self.board[previous_move.start_row][previous_move.start_col] = previous_move.piece_moved
            self.board[previous_move.end_row][previous_move.end_col] = previous_move.piece_captured

    def get_valid_moves(self):
        """
        All moves considering checks
        """
        

    
    def get_all_possible_moves(self):
        """
        All moves without considering checks
        """
        


class Move:

    ranksToRows = {
        '1' :7,
        '2' :6,
        '3' :5,
        '4' :4,
        '5' :3,
        '6' :2,
        '7' :1,
        '8' :0
    }
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {
        'a' :7,
        'b' :6,
        'c' :5,
        'd' :4,
        'e' :3,
        'f' :2,
        'g' :1,
        'h' :0
    }
    colsToFiles = {v: k for k, v in filesToCols.items()}


    def __init__(self, start_sq, end_sq, board):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]

    def get_chess_notation(self):
        self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col) 

    def get_rank_file(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
