import fen
from main import DIMENSION


class GameState:
    def __init__(self):
        self.board = fen.fen_to_board('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR')
        self.move_functions = {
            'P': self.get_pawn_moves,
            'R': self.get_rook_moves,
            'N': self.get_knight_moves,
            'B': self.get_bishop_moves,
            'Q': self.get_queen_moves,
            'K': self.get_king_moves
        }
        
        self.white_to_move = True
        self.move_log = []



    def make_move(self,move):
        """
        Use Move object to make a move, does not work for castling and en passant
        """
        self.board[move.start_row][move.start_col] = '--'
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move
        print(move.get_chess_notation())


    def undo_move(self):
        if len(self.move_log) > 0:
            previous_move = self.move_log.pop()
            self.board[previous_move.start_row][previous_move.start_col] = previous_move.piece_moved
            self.board[previous_move.end_row][previous_move.end_col] = previous_move.piece_captured
            self.white_to_move = not self.white_to_move

    def get_valid_moves(self):
        """
        All moves considering checks
        """
        return self.get_all_possible_moves()

    
    def get_all_possible_moves(self):
        """
        All moves without considering checks
        """
        moves = []
        for r in range(DIMENSION):
            for c in range(DIMENSION):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.white_to_move) or (turn == 'b' and not self.white_to_move):
                    piece = self.board[r][c][1]
                    self.move_functions[piece](r,c,moves)
                    
        return moves


    def get_pawn_moves(self,r,c,moves):
        if self.white_to_move: # White pawn logic
            if self.board[r-1][c] == '--': # All 1-square pawn advance
                moves.append(Move((r,c), (r-1,c), self.board))
                if r == 6 and self.board[r-2][c] == '--': # 2-square pawn advance
                    moves.append(Move((r,c), (r-2,c), self.board))
            if c-1 >= 0:
                if self.board[r-1][c-1][0] == 'b':
                    moves.append(Move((r,c), (r-1,c-1), self.board))

            if c+1 <= 7:
                if self.board[r-1][c+1][0] == 'b':
                    moves.append(Move((r,c), (r-1,c+1), self.board))

        else: # Black pawn logic
            if self.board[r+1][c] == '--': # All 1-square pawn advance
                moves.append(Move((r,c), (r+1,c), self.board))
                if r == 1 and self.board[r+2][c] == '--': # 2-square pawn advance
                    moves.append(Move((r,c), (r+2,c), self.board))
            if c-1 >= 0:
                if self.board[r+1][c-1][0] == 'w':
                    moves.append(Move((r,c), (r+1,c-1), self.board))

            if c+1 <= 7:
                if self.board[r+1][c+1][0] == 'w':
                    moves.append(Move((r,c), (r+1,c+1), self.board))
        # add pawn promotions later
        # add en passant later

    def get_rook_moves(self,r,c,moves):
        directions = [(-1,0), (0,1), (1,0), (0,-1)]
        enemy_colour = 'b' if self.white_to_move else 'w'
        for d in directions:
            for i in range(1,8):
                end_r = r + d[0] * i
                end_c = c + d[1] * i
                if 0 <= end_r <= 7 and 0 <= end_c <= 7: # Set boundaries
                    end_piece = self.board[end_r][end_c]
                    if end_piece == '--': # Empty space
                        moves.append(Move((r,c), (end_r, end_c), self.board))
                    elif end_piece[0] == enemy_colour: # Enemy piece
                        moves.append(Move((r,c), (end_r, end_c), self.board))
                        break
                    else: # Own piece
                        break
                else: # Beyond board boundaries
                    break
        
        pass
    # while loop, condition rcboundaries, same/diff color pc
     

    def get_knight_moves(self,r,c,moves):
        pass

    def get_bishop_moves(self,r,c,moves):
        pass

    def get_queen_moves(self,r,c,moves):
        pass

    def get_king_moves(self,r,c,moves):
        pass


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
        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col
        
    def __eq__(self, other):
        """
        Equals method
        """
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False

    def get_chess_notation(self):
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col) 

    def get_rank_file(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
