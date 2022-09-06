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
        self.white_king_pos = (7,4)
        self.black_king_pos = (0,4)


    def make_move(self,move):
        """
        Use Move object to make a move, does not work for castling and en passant
        """
        self.board[move.start_row][move.start_col] = '--'
        self.board[move.tgt_row][move.tgt_col] = move.piece_moved
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move
        print(move.get_chess_notation())
        if move.piece_moved == 'wK':
            self.white_king_pos = move.tgt_sq
        elif move.piece_moved == 'bK':
            self.black_king_pos = move.tgt_sq


    def undo_move(self):
        if len(self.move_log) > 0:
            previous_move = self.move_log.pop()
            self.board[previous_move.start_row][previous_move.start_col] = previous_move.piece_moved
            self.board[previous_move.tgt_row][previous_move.tgt_col] = previous_move.piece_captured
            if previous_move.piece_moved == 'wK':
                self.white_king_pos = previous_move.start_sq
            elif previous_move.piece_moved == 'bK':
                self.black_king_pos = previous_move.start_sq
            self.white_to_move = not self.white_to_move

    def get_valid_moves(self):
        """
        All moves considering checks
        """
        all_possible_moves = self.get_all_possible_moves()
        if self.check_for_checks():
            print('CHECK')
        return self.get_all_possible_moves()

    # check for checks on king relative to king
    # if check, disable move if moving turn
    
    # cfc on enemy when move is made

    def check_for_checks(self):
        # for king piece, check rook, pawn, knight or bishop attack    

        # check player team
        if self.white_to_move:
            r = self.white_king_pos[0]
            c = self.white_king_pos[1]
            enemy_colour = 'b'
            pawn_directions = [(-1,-1), (-1,1)]
        else:
            r = self.black_king_pos[0]
            c = self.black_king_pos[1]
            enemy_colour = 'w'
            pawn_directions = [(1,-1), (1,1)]


        # Rook / Queen checks
        directions = [(-1,0), (0,1), (1,0), (0,-1)]
        for d in directions:
            for i in range(1,8):
                tgt_r = r + d[0] * i
                tgt_c = c + d[1] * i
                if 0 <= tgt_r <= 7 and 0 <= tgt_c <= 7: # Set boundaries
                    tgt_piece = self.board[tgt_r][tgt_c]
                    if tgt_piece[1] in ['R','Q']: # Empty space
                        return True
                else: # Beyond board boundaries
                    break

        # Bishop / Queen checks
        directions = [(-1,-1), (-1,1), (1,-1), (1,1)]
        for d in directions:
            for i in range(1,8):
                tgt_r = r + d[0] * i
                tgt_c = c + d[1] * i
                if 0 <= tgt_r <= 7 and 0 <= tgt_c <= 7: # Set boundaries
                    tgt_piece = self.board[tgt_r][tgt_c]
                    if tgt_piece[1] in ['B','Q']: # Empty space
                        return True
                else: # Beyond board boundaries
                    break

        # Knight checks
        directions = [(-2,-1), (-1,-2), (1,-2), (2,-1), (2,1), (1,2), (-1,2), (-2,1)]
        for d in directions:
            tgt_r = r + d[0]
            tgt_c = c + d[1]
            if 0 <= tgt_r <= 7 and 0 <= tgt_c <= 7: 
                tgt_piece = self.board[tgt_r][tgt_c]
                if tgt_piece[1] == 'N' or tgt_piece[0] == enemy_colour:
                    return True

        # Pawn checks
        for d in pawn_directions:
            tgt_r = r + d[0]
            tgt_c = c + d[1]
            if 0 <= tgt_r <= 7 and 0 <= tgt_c <= 7:
                tgt_piece = self.board[tgt_r][tgt_c]
                if tgt_piece[1] == 'P' or tgt_piece[0] == enemy_colour:
                    return True

        # End
        return False
    
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
                tgt_r = r + d[0] * i
                tgt_c = c + d[1] * i
                if 0 <= tgt_r <= 7 and 0 <= tgt_c <= 7: # Set boundaries
                    tgt_piece = self.board[tgt_r][tgt_c]
                    if tgt_piece == '--': # Empty space
                        moves.append(Move((r,c), (tgt_r, tgt_c), self.board))
                    elif tgt_piece[0] == enemy_colour: # Enemy piece
                        moves.append(Move((r,c), (tgt_r, tgt_c), self.board))
                        break
                    else: # Own piece
                        break
                else: # Beyond board boundaries
                    break
             
    def get_knight_moves(self,r,c,moves):
        directions = [(-2,-1), (-1,-2), (1,-2), (2,-1), (2,1), (1,2), (-1,2), (-2,1)]
        enemy_colour = 'b' if self.white_to_move else 'w'
        for d in directions:
            tgt_r = r + d[0]
            tgt_c = c + d[1]
            if 0 <= tgt_r <= 7 and 0 <= tgt_c <= 7: 
                tgt_piece = self.board[tgt_r][tgt_c]
                if tgt_piece == '--' or tgt_piece[0] == enemy_colour:
                    moves.append(Move((r,c), (tgt_r,tgt_c), self.board))

    def get_bishop_moves(self,r,c,moves):
        directions = [(-1,-1), (-1,1), (1,-1), (1,1)]
        enemy_colour = 'b' if self.white_to_move else 'w'
        for d in directions:
            for i in range(1,8):
                tgt_r = r + d[0] * i
                tgt_c = c + d[1] * i
                if 0 <= tgt_r <= 7 and 0 <= tgt_c <= 7: # Set boundaries
                    tgt_piece = self.board[tgt_r][tgt_c]
                    if tgt_piece == '--': # Empty space
                        moves.append(Move((r,c), (tgt_r, tgt_c), self.board))
                    elif tgt_piece[0] == enemy_colour: # Enemy piece
                        moves.append(Move((r,c), (tgt_r, tgt_c), self.board))
                        break
                    else: # Own piece
                        break
                else: # Beyond board boundaries
                    break

    def get_queen_moves(self,r,c,moves):
        directions = [(-1,0), (0,1), (1,0), (0,-1), (-1,-1), (-1,1), (1,-1), (1,1)]
        enemy_colour = 'b' if self.white_to_move else 'w'
        for d in directions:
            for i in range(1,8):
                tgt_r = r + d[0] * i
                tgt_c = c + d[1] * i
                if 0 <= tgt_r <= 7 and 0 <= tgt_c <= 7: # Set boundaries
                    tgt_piece = self.board[tgt_r][tgt_c]
                    if tgt_piece == '--': # Empty space
                        moves.append(Move((r,c), (tgt_r, tgt_c), self.board))
                    elif tgt_piece[0] == enemy_colour: # Enemy piece
                        moves.append(Move((r,c), (tgt_r, tgt_c), self.board))
                        break
                    else: # Own piece
                        break
                else: # Beyond board boundaries
                    break

    def get_king_moves(self,r,c,moves):
        directions = [(-1,0), (0,1), (1,0), (0,-1), (-1,-1), (-1,1), (1,-1), (1,1)]
        enemy_colour = 'b' if self.white_to_move else 'w'
        for d in directions:
            tgt_r = r + d[0]
            tgt_c = c + d[1]
            if 0 <= tgt_r <= 7 and 0 <= tgt_c <= 7: # Set boundaries
                tgt_piece = self.board[tgt_r][tgt_c]
                if tgt_piece == '--' or tgt_piece[0] == enemy_colour: # Empty space
                    moves.append(Move((r,c), (tgt_r, tgt_c), self.board))
                

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


    def __init__(self, start_sq, tgt_sq, board):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.tgt_row = tgt_sq[0]
        self.tgt_col = tgt_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.tgt_row][self.tgt_col]
        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.tgt_row * 10 + self.tgt_col
        
    def __eq__(self, other):
        """
        Equals method
        """
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False

    def get_chess_notation(self):
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.tgt_row, self.tgt_col) 

    def get_rank_file(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
