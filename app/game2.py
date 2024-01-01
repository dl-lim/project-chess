from app.config import GameConfig
from app.game_state import GameState
from app.projection_engine import Move
import pygame

from icecream import ic

class ChessGame:
    def __init__(self) -> None:
        pass

    def run(self):
        GameConfig.reset_clock()
        run = True
        gs = GameState()
        valid_moves = gs.get_valid_moves()
        sq_selected = ()
        player_clicks = []
        move_made = False


        while run:
            GameConfig.CLOCK.tick(GameConfig.FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    location = pygame.mouse.get_pos()
                    col = location[0] // GameConfig.TILE_WIDTH
                    row = location[1] // GameConfig.TILE_WIDTH
                    if sq_selected == (row, col): # If same square was selected, reset
                        sq_selected = ()
                        player_clicks = []
                    else: # If another square
                        sq_selected = (row, col)
                        player_clicks.append(sq_selected)
                    
                    if len(player_clicks) == 2: # Second click submitted
                        move = Move(player_clicks[0], player_clicks[1], gs.board)
                        
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]: # use this check in order to take moves from valid moves instead of mouse click
                                gs.make_move(valid_moves[i])
                                move_made = True
                                ANIMATE = True
                                sq_selected = ()
                                player_clicks = []
                        
                        if not move_made:
                            player_clicks = [sq_selected]
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_z:
                        gs.undo_move()
                        move_made = True
                        ANIMATE = False

                    elif event.key == pygame.K_r:
                        GameConfig.reset_clock()
                        run = True
                        gs = GameState()
                        valid_moves = gs.get_valid_moves()
                        sq_selected = ()
                        player_clicks = []
                        move_made = False
            
            if move_made:
                if ANIMATE:
                    self._animate_moves(gs.move_log[-1], GameConfig.WIN, gs.board)
                valid_moves = gs.get_valid_moves()
                move_made = False
            
            self._draw_gamestate(gs, valid_moves, sq_selected)
            pygame.display.flip()
        pygame.quit()

    def _draw_gamestate(self, gs, valid_moves, sq_selected):
        self._draw_board()
        self._draw_pieces(gs.board)
        self._draw_square_highlights(gs, valid_moves, sq_selected)

    def _draw_board(self):
        for row in range(GameConfig.DIMENSION):
            for col in range(GameConfig.DIMENSION):
                squareColour = GameConfig.LIGHT if ((col + row) % 2 == 0) else GameConfig.DARK
                pygame.draw.rect(GameConfig.WIN, squareColour, pygame.Rect(col*GameConfig.TILE_WIDTH, row*GameConfig.TILE_WIDTH, GameConfig.TILE_WIDTH, GameConfig.TILE_WIDTH))

    def _draw_pieces(self, board):
        for rank in range(GameConfig.DIMENSION):
            for file in range(GameConfig.DIMENSION):
                piece = board[rank][file]
                if piece != '--':
                    GameConfig.WIN.blit(GameConfig.IMAGES[piece], pygame.Rect(file*GameConfig.TILE_WIDTH, rank*GameConfig.TILE_WIDTH, GameConfig.TILE_WIDTH, GameConfig.TILE_WIDTH))    

    def _draw_square_highlights(self, gs, valid_moves, sq_selected):
        if sq_selected != ():
            r,c = sq_selected
            if gs.board[r][c][0] == ('w' if gs.white_to_move else 'b'):
                sq = pygame.Surface((GameConfig.TILE_WIDTH, GameConfig.TILE_WIDTH))
                sq.set_alpha(98)
                sq.fill('#f28095')
                GameConfig.WIN.blit(sq, (c * GameConfig.TILE_WIDTH, r * GameConfig.TILE_WIDTH))
                sq.fill('#f2b380')
                for move in valid_moves:
                    if move.start_row == r and move.start_col == c:
                        GameConfig.WIN.blit(sq, (move.end_col * GameConfig.TILE_WIDTH, move.end_row * GameConfig.TILE_WIDTH))


    def _animate_moves(self, move, board):
        dr = move.end_row - move.start_row
        dc = move.end_col - move.start_col
        frames_per_sq = 3
        frame_count = (abs(dr) + abs(dc)) * frames_per_sq
        for frame in range(frame_count + 1):
            r,c = (move.start_row + dr * frame / frame_count,move.start_col + dc * frame / frame_count)
            self._draw_board(GameConfig.WIN)
            self._draw_pieces(GameConfig.WIN,board)
            colour = GameConfig.LIGHT if ((move.end_col + move.end_row) % 2 == 0) else GameConfig.DARK
            end_square = pygame.Rect(move.end_col * GameConfig.TILE_WIDTH, move.end_row * GameConfig.TILE_WIDTH, GameConfig.TILE_WIDTH, GameConfig.TILE_WIDTH)
            pygame.draw.rect(GameConfig.WIN,colour, end_square)

            # draw captured piece
            if move.piece_captured != '--':
                if move.is_en_passant:
                    en_passant_row = (move.end_row - 1) if move.piece_moved[0] == 'b' else (move.end_row + 1)
                    end_square = pygame.Rect(move.end_col * GameConfig.TILE_WIDTH, en_passant_row * GameConfig.TILE_WIDTH, GameConfig.TILE_WIDTH, GameConfig.TILE_WIDTH)
                GameConfig.WIN.blit(GameConfig.IMAGES[move.piece_captured], end_square)

            # draw moving piece
            if move.piece_moved != '--':
                GameConfig.WIN.blit(GameConfig.IMAGES[move.piece_moved], pygame.Rect(c * GameConfig.TILE_WIDTH, r * GameConfig.TILE_WIDTH, GameConfig.TILE_WIDTH, GameConfig.TILE_WIDTH))
            pygame.display.flip()
            GameConfig.CLOCK.tick(60)



    