class FENConverter:
    piece_lookup = {
        'r' : 'bR',
        'n' : 'bN',
        'b' : 'bB',
        'k' : 'bK',
        'q' : 'bQ',
        'p' : 'bP',
        'R' : 'wR',
        'N' : 'wN',
        'B' : 'wB',
        'K' : 'wK',
        'Q' : 'wQ',
        'P' : 'wP',
        'bR' : 'r',
        'bN' : 'n',
        'bB' : 'b',
        'bK' : 'k',
        'bQ' : 'q',
        'bP' : 'p',
        'wR' : 'R',
        'wN' : 'N',
        'wB' : 'B',
        'wK' : 'K',
        'wQ' : 'Q',
        'wP' : 'P' 
    }

    @classmethod
    def fen_to_board(cls, fen_string):
        board = []
        ranks = fen_string.split('/')
        for rank in range(8):
            board_file = [] 
            board_file_cur = 0
            for s in ranks[rank]:
                if s.isnumeric():
                    for _ in range(int(s)):
                        board_file.append('--')
                        board_file_cur += 1
                else:
                    piece = cls.piece_lookup[s]
                    board_file.append(piece)
                    board_file_cur += 1
            board.append(board_file)
        return board

    @classmethod
    def board_to_fen(cls, board):
        fen_string = ''
        for rank in board:
            fen_rank = ''
            count = 0
            for square in rank:
                if square == '--':
                    count += 1
                else:
                    if count != 0:
                        fen_rank += str(count)
                        count = 0
                    fen_rank += cls.piece_lookup[square]
            if count != 0:
                fen_rank += str(count)

            if fen_string == '':
                fen_string = fen_rank
            else:
                fen_string += '/' + fen_rank
        return fen_string
