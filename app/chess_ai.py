import random
from app.projection_engine import Projection

from icecream import ic

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

class BasicAI:
    def __init__(self, game_state):
        self.gs = game_state
        self.projection = self.gs.get_projection_at_current_state()
        self.valid_moves = self.projection.get_valid_moves()


class RandomAI(BasicAI):
    def find_move(self):
        return random.choice(self.valid_moves)

class GreedyAI(BasicAI):
    def find_move(self):
        score_factor = 1 if self.projection.white_to_move else -1
        my_maxscore = CHECKMATE_SCORE
        best_move = None
        random.shuffle(self.valid_moves)

        for curr_move in self.valid_moves:
            self.projection.make_projection(curr_move)
            opponent_moves = self.projection.get_valid_moves()
            opponent_maxscore = -CHECKMATE_SCORE
            for move in opponent_moves:
                self.projection.make_projection(move)
                if self.projection.checkmate:
                    score = -score_factor * CHECKMATE_SCORE
                elif self.projection.stalemate:
                    score = STALEMATE_SCORE
                else:
                    score = -score_factor * self.score_material()
                if score > opponent_maxscore:
                    opponent_maxscore = score
                self.projection.undo_projection()
            if opponent_maxscore < my_maxscore:
                my_maxscore = opponent_maxscore
                best_move = curr_move
            self.projection.undo_projection()
        return best_move

    def score_material(self):
        score = 0
        for row in self.projection.board:
            for square in row:
                if square[0] == 'w':
                    score += piece_score[square[1]]
                elif square[0] == 'b':
                    score -= piece_score[square[1]]
        return score