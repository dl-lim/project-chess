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

    def make_move(self,move):
        """
        Use Move object to make a move, does not work for castling and en passant
        """
        self.board[move.start_row][move.start_col] = '--'
        self.board[move.end_row][move.end_col] = move.piece_moved
        if self.check_for_checks(move):
            print('CHECK')
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move
        print(move.get_chess_notation())
        if move.piece_moved == 'wK':
            self.white_king_pos = move.end_sq
        elif move.piece_moved == 'bK':
            self.black_king_pos = move.end_sq

    def undo_move(self):
        if len(self.move_log) > 0:
            previous_move = self.move_log.pop()
            self.board[previous_move.start_row][previous_move.start_col] = previous_move.piece_moved
            self.board[previous_move.end_row][previous_move.end_col] = previous_move.piece_captured
            if previous_move.piece_moved == 'wK':
                self.white_king_pos = previous_move.start_sq
            elif previous_move.piece_moved == 'bK':
                self.black_king_pos = previous_move.start_sq
            self.white_to_move = not self.white_to_move

    def get_valid_moves(self):
        """
        All moves considering checks
        """
        ## This section requires debugging
        possible_moves = self.get_all_possible_moves()
        for m in range(len(possible_moves)-1, -1, -1):
            move = possible_moves[m]
            if self.check_for_checks(move):
                possible_moves.pop(m)
        return possible_moves

    # check for checks on king relative to king
    # if check, disable move if moving turn
    
    # cfc on enemy when move is made
    def check_for_checks(self, move):
        # for king piece, check rook, pawn, knight or bishop attack    
        
        # test the move for checks
        test_board = copy.deepcopy(self.board)
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
            enemy_colour = 'b'
            pawn_directions = [(-1,-1), (-1,1)]
        else:
            r = test_black_king_pos[0]
            c = test_black_king_pos[1]
            enemy_colour = 'w'
            pawn_directions = [(1,-1), (1,1)]

        if fen.board_to_fen(self.board) == 'rnbqkbnr/pppp1ppp/8/4p2Q/4P3/8/PPPP1PPP/RNB1KBNR':
            for row in test_board:
                print(row)
            print('-----------------------------------------')
            print(enemy_colour)

        # Rook / Queen checks
        directions = [(-1,0), (0,1), (1,0), (0,-1)]
        for d in directions:
            for i in range(1,8):
                tgt_r = r + d[0] * i
                tgt_c = c + d[1] * i
                if 0 <= tgt_r <= 7 and 0 <= tgt_c <= 7: # Set boundaries
                    tgt_piece = test_board[tgt_r][tgt_c]
                    if tgt_piece == '--':
                        continue
                    else:
                        if tgt_piece[0] != enemy_colour:
                            break
                        elif tgt_piece[0] == enemy_colour and tgt_piece[1] in ['R','Q']:
                            print('rq hit')
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
                    tgt_piece = test_board[tgt_r][tgt_c]
                    if tgt_piece == '--':
                        continue
                    else:
                        if tgt_piece[0] != enemy_colour:
                            break
                        elif tgt_piece[0] == enemy_colour and tgt_piece[1] in ['B','Q']: # Empty space
                            print('bq hit')
                            return True
                else: # Beyond board boundaries
                    break

        # Knight checks
        directions = [(-2,-1), (-1,-2), (1,-2), (2,-1), (2,1), (1,2), (-1,2), (-2,1)]
        for d in directions:
            tgt_r = r + d[0]
            tgt_c = c + d[1]
            if 0 <= tgt_r <= 7 and 0 <= tgt_c <= 7: 
                tgt_piece = test_board[tgt_r][tgt_c]
                if tgt_piece[0] == enemy_colour and tgt_piece[1] == 'N':
                    print('N hit')
                    return True

        # Pawn checks
        for d in pawn_directions:
            tgt_r = r + d[0]
            tgt_c = c + d[1]
            if 0 <= tgt_r <= 7 and 0 <= tgt_c <= 7:
                tgt_piece = test_board[tgt_r][tgt_c]
                if tgt_piece[0] == enemy_colour and tgt_piece[1] == 'P':
                    print('pawn hit')
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


    def __init__(self, start_sq, end_sq, board):
        self.start_sq = start_sq
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_sq = end_sq
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
