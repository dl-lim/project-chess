import random


CHECKMATE_SCORE = 1000
STALEMATE_SCORE = 0

piece_score = {
        "P": 1,
        "R": 5,
        "N": 3,
        "B": 3,
        "Q": 9,
        "K": 0,
    }


def find_random_move(valid_moves):
    return valid_moves[random.randint(0, len(valid_moves) - 1)]

def find_greedy_move(gs, valid_moves):
    score_factor = 1 if gs.white_to_move else -1
    my_maxscore = CHECKMATE_SCORE
    best_move = None
    random.shuffle(valid_moves)
    for curr_move in valid_moves:
        gs.project_move(curr_move)
        opponent_moves = gs.get_valid_moves()
        opponent_maxscore = -CHECKMATE_SCORE
        for move in opponent_moves:
            gs.project_move(move)
            if gs.checkmate:
                score = -score_factor * CHECKMATE_SCORE
            elif gs.stalemate:
                score = STALEMATE_SCORE
            else:
                score = -score_factor * score_material(gs.projected_board)
            if score > opponent_maxscore:
                opponent_maxscore = score
            gs.undo_projection()
        if opponent_maxscore < my_maxscore:
            my_maxscore = opponent_maxscore
            best_move = curr_move
        gs.undo_projection()
    return best_move

def score_material(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += piece_score[square[1]]
            elif square[0] == 'b':
                score -= piece_score[square[1]]
    return score