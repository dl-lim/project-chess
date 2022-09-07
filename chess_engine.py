import fen
import copy
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
        self.en_passant_possible = ()
        self.curr_castling_rights = CastlingRights()
        self.castling_rights_log = [CastlingRights()]
        self.in_check = False

    def make_move(self,move):
        """
        Use Move object to make a move
        """
        self.board[move.start_row][move.start_col] = '--'
        self.board[move.end_row][move.end_col] = move.piece_moved
        
        if move.piece_moved == 'wK':
            self.white_king_pos = move.end_sq
        elif move.piece_moved == 'bK':
            self.black_king_pos = move.end_sq
        print(move.get_chess_notation())
        
        # Checks if move pushes pawns to promotion
        if move.is_pawn_promotion:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + 'Q' # to do this choice on main.py to avoid changing the Move class
        
        # Removes enemy pawn behind en passant
        if move.is_en_passant:
            self.board[move.start_row][move.end_col] = '--'
        
        # Generates en passant posibilities
        if move.piece_moved[1] == 'P' and abs(move.start_row - move.end_row) == 2:
            self.en_passant_possible = ((move.start_row + move.end_row) // 2, move.start_col)
        else:
            self.en_passant_possible = ()

        # Castling move
        if move.is_castling:
            if move.end_col - move.start_col > 0: # kingside castle move
                self.board[move.end_row][move.end_col-1] = self.board[move.end_row][move.end_col+1]
                self.board[move.end_row][move.end_col+1] = '--'
            else: # queenside
                self.board[move.end_row][move.end_col+1] = self.board[move.end_row][move.end_col-2]
                self.board[move.end_row][move.end_col-2] = '--'
        
        # Update Castling Rights
        self.update_castling_rights(move)

        # Append to logs
        self.castling_rights_log.append(CastlingRights(self.curr_castling_rights.wks, self.curr_castling_rights.wqs,
                                        self.curr_castling_rights.bks, self.curr_castling_rights.bqs))
        self.move_log.append(move)

        # Change to other team before checking for checks
        self.white_to_move = not self.white_to_move

        # Check for checks or checkmate or stalemate
        if self.check_for_checks() or len(self.get_valid_moves()) == 0:
            self.check_for_checkmate()
        else:
            self.in_check = False

    def undo_move(self):
        if len(self.move_log) > 0:
            prev_move = self.move_log.pop()
            self.board[prev_move.start_row][prev_move.start_col] = prev_move.piece_moved
            self.board[prev_move.end_row][prev_move.end_col] = prev_move.piece_captured
            
            if prev_move.piece_moved == 'wK':
                self.white_king_pos = prev_move.start_sq
            elif prev_move.piece_moved == 'bK':
                self.black_king_pos = prev_move.start_sq
            
            if prev_move.is_en_passant:
                self.board[prev_move.end_row][prev_move.end_col] = '--'
                self.board[prev_move.start_row][prev_move.end_col] = prev_move.piece_captured
                self.en_passant_possible = (prev_move.end_row, prev_move.end_col)

            if prev_move.is_castling:
                if prev_move.end_col - prev_move.start_col > 0: # kingside castle move
                    self.board[prev_move.end_row][prev_move.end_col+1] = self.board[prev_move.end_row][prev_move.end_col-1]
                    self.board[prev_move.end_row][prev_move.end_col-1] = '--'
                else: # queenside
                    self.board[prev_move.end_row][prev_move.end_col-2] = self.board[prev_move.end_row][prev_move.end_col+1]
                    self.board[prev_move.end_row][prev_move.end_col+1] = '--'

            self.castling_rights_log.pop()
            self.curr_castling_rights = self.castling_rights_log[-1]

            self.white_to_move = not self.white_to_move

    def get_valid_moves(self):
        """
        All moves considering checks
        """
        temp_castling_rights = CastlingRights(self.curr_castling_rights.wks, self.curr_castling_rights.wqs,
                                          self.curr_castling_rights.bks, self.curr_castling_rights.bqs)

        possible_moves = self.get_all_possible_moves()
        for m in range(len(possible_moves)-1, -1, -1):
            move = possible_moves[m]
            if self.check_for_checks(move):
                possible_moves.pop(m)

        self.curr_castling_rights = temp_castling_rights
        return possible_moves

    def update_castling_rights(self,move):
        if move.piece_moved == 'wK':
            self.curr_castling_rights.wks = False
            self.curr_castling_rights.wqs = False
        elif move.piece_moved == 'bK':
            self.curr_castling_rights.bks = False
            self.curr_castling_rights.bqs = False
        elif move.piece_moved == 'wR':
            if move.start_col == 0:
                self.curr_castling_rights.wqs = False
            elif move.start_col == 7:
                self.curr_castling_rights.wks = False
        elif move.piece_moved == 'bR':
            if move.start_col == 0:
                self.curr_castling_rights.bqs = False
            elif move.start_col == 7:
                self.curr_castling_rights.bks = False

        if move.piece_captured == 'wR':
            if move.end_col == 0:
                self.curr_castling_rights.wqs = False
            elif move.end_col == 7:
                self.curr_castling_rights.wks = False
        elif move.piece_captured == 'bR':
            if move.end_col == 0:
                self.curr_castling_rights.bqs = False
            elif move.end_col == 7:
                self.curr_castling_rights.bks = False

    def square_under_attack(self,r,c,board=None):
        if board == None:
            board = self.board

        if self.white_to_move:
            enemy_colour = 'b'
            pawn_directions = [(-1,-1), (-1,1)]
        else:
            enemy_colour = 'w'
            pawn_directions = [(1,-1), (1,1)]

        # Rook / Queen checks
        directions = [(-1,0), (0,1), (1,0), (0,-1)]
        for d in directions:
            for i in range(1,8):
                tgt_r = r + d[0] * i
                tgt_c = c + d[1] * i
                if 0 <= tgt_r <= 7 and 0 <= tgt_c <= 7: # Set boundaries
                    tgt_piece = board[tgt_r][tgt_c]
                    if tgt_piece == '--':
                        continue
                    else:
                        if tgt_piece[0] != enemy_colour:
                            break
                        elif tgt_piece[0] == enemy_colour and tgt_piece[1] in ['R','Q']:
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
                    tgt_piece = board[tgt_r][tgt_c]
                    if tgt_piece == '--':
                        continue
                    else:
                        if tgt_piece[0] != enemy_colour:
                            break
                        elif tgt_piece[0] == enemy_colour and tgt_piece[1] in ['B','Q']: # Empty space
                            return True
                else: # Beyond board boundaries
                    break

        # Knight checks
        directions = [(-2,-1), (-1,-2), (1,-2), (2,-1), (2,1), (1,2), (-1,2), (-2,1)]
        for d in directions:
            tgt_r = r + d[0]
            tgt_c = c + d[1]
            if 0 <= tgt_r <= 7 and 0 <= tgt_c <= 7: 
                tgt_piece = board[tgt_r][tgt_c]
                if tgt_piece[0] == enemy_colour and tgt_piece[1] == 'N':
                    return True

        # Pawn checks
        for d in pawn_directions:
            tgt_r = r + d[0]
            tgt_c = c + d[1]
            if 0 <= tgt_r <= 7 and 0 <= tgt_c <= 7:
                tgt_piece = board[tgt_r][tgt_c]
                if tgt_piece[0] == enemy_colour and tgt_piece[1] == 'P':
                    return True

        # King checks
        directions = [(-1,0), (0,1), (1,0), (0,-1), (-1,-1), (-1,1), (1,-1), (1,1)]
        for d in directions:
            tgt_r = r + d[0]
            tgt_c = c + d[1]
            if 0 <= tgt_r <= 7 and 0 <= tgt_c <= 7: 
                tgt_piece = board[tgt_r][tgt_c]
                if tgt_piece[0] == enemy_colour and tgt_piece[1] == 'K':
                    return True

        # End
        return False
        
    def check_for_checks(self, move=None):
        # for king piece, check rook, pawn, knight or bishop attack    
        
        # test the move for checks
        test_board = copy.deepcopy(self.board)
        if move:
            test_board[move.start_row][move.start_col] = '--'
            test_board[move.end_row][move.end_col] = move.piece_moved
        
        test_white_king_pos, test_black_king_pos = None, None
        for row in range(DIMENSION):
            for col in range(DIMENSION):
                if test_white_king_pos and test_black_king_pos:
                    break
                if test_board[row][col][1] == 'K':
                    if test_board[row][col][0] == 'w':
                        test_white_king_pos = (row,col)
                    else:
                        test_black_king_pos = (row,col)

        # check player team
        if self.white_to_move:
            r = test_white_king_pos[0]
            c = test_white_king_pos[1]
        else:
            r = test_black_king_pos[0]
            c = test_black_king_pos[1]

        return self.square_under_attack(r,c,test_board)


    def get_all_possible_moves(self):
        """
        All moves without considering checks
        """
        moves = []
        for r in range(DIMENSION):
            for c in range(DIMENSION):
                if self.board[r][c] == '--':
                    continue
                else:
                    team = self.board[r][c][0]
                    if (team == 'w' and self.white_to_move) or (team == 'b' and not self.white_to_move):
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
                elif (r-1,c-1) == self.en_passant_possible:
                    moves.append(Move((r,c), (r-1,c-1), self.board, is_en_passant=True))
            
            if c+1 <= 7:
                if self.board[r-1][c+1][0] == 'b':
                    moves.append(Move((r,c), (r-1,c+1), self.board))
                elif (r-1,c+1) == self.en_passant_possible:
                    moves.append(Move((r,c), (r-1,c+1), self.board, is_en_passant=True))

        else: # Black pawn logic
            if self.board[r+1][c] == '--': # All 1-square pawn advance
                moves.append(Move((r,c), (r+1,c), self.board))
                if r == 1 and self.board[r+2][c] == '--': # 2-square pawn advance
                    moves.append(Move((r,c), (r+2,c), self.board))
            if c-1 >= 0:
                if self.board[r+1][c-1][0] == 'w':
                    moves.append(Move((r,c), (r+1,c-1), self.board))
                elif (r+1,c-1) == self.en_passant_possible:
                    moves.append(Move((r,c), (r+1,c-1), self.board, is_en_passant=True))

            if c+1 <= 7:
                if self.board[r+1][c+1][0] == 'w':
                    moves.append(Move((r,c), (r+1,c+1), self.board))
                elif (r+1,c+1) == self.en_passant_possible:
                    moves.append(Move((r,c), (r+1,c+1), self.board, is_en_passant=True))

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
        self.get_castling_moves(r,c,moves)

    def get_castling_moves(self,r,c,moves):
        if not self.in_check:
            if (self.white_to_move and self.curr_castling_rights.wks) or ((not self.white_to_move) and self.curr_castling_rights.bks):
                self.get_kingside_castling_moves(r,c,moves)
            if (self.white_to_move and self.curr_castling_rights.wqs) or ((not self.white_to_move) and self.curr_castling_rights.bqs):
                self.get_queenside_castling_moves(r,c,moves)
    
    def get_kingside_castling_moves(self,r,c,moves):
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.square_under_attack(r, c+1) and not self.square_under_attack(r,c+2):
                moves.append(Move((r,c),(r,c+2), self.board, is_castling=True))

    def get_queenside_castling_moves(self,r,c,moves):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':
            if not self.square_under_attack(r, c-1) and not self.square_under_attack(r,c-2):
                moves.append(Move((r,c),(r,c-2), self.board, is_castling=True))


    def check_for_checkmate(self):
        current_moves = self.get_valid_moves()

        if len(current_moves) == 0 and not self.check_for_checks():
            print('Stalemate')

        elif len(current_moves) == 0 and self.check_for_checks():
            winner = 'Black' if self.white_to_move else 'White'
            loser = 'White' if self.white_to_move else 'Black'
            self.in_check = True
            print('CHECKMATE for', loser)
            print(winner, 'wins!')
        else:
            enemy_team = 'White' if self.white_to_move else 'Black'
            self.in_check = True
            print('CHECK on', enemy_team)

class CastlingRights:
    def __init__(self, wks=True, wqs=True, bks=True, bqs=True):
        self.wks = wks
        self.wqs = wqs
        self.bks = bks
        self.bqs = bqs

    def get_rights(self):
        cr_id = str(self.wks * 1000 + self.wqs * 100 + self.bks * 10 + self.bqs * 1).zfill(4)
        print(cr_id)
        return cr_id

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


    def __init__(self, start_sq, end_sq, board, is_en_passant=False, is_castling=False):
        self.start_sq = start_sq
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_sq = end_sq
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.move_id = str(self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col).zfill(4)
        
        # Pawn Promotions
        self.is_pawn_promotion = (self.piece_moved == 'wP' and self.end_row == 0) or (self.piece_moved == 'bP' and self.end_row == 7)
        
        # En Passant
        self.is_en_passant = is_en_passant
        if self.is_en_passant:
            self.piece_captured = 'wP' if self.piece_moved == 'bP' else 'bP'

        # Castling
        self.is_castling = is_castling

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
