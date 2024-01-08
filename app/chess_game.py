import pygame

from app.config import GAME_CONFIG
from app.game_state import GameState
from app.projection_engine import Move
from app.chess_ai import RandomAI # find_random_move, find_greedy_move

from multiprocessing import Process, Queue


from icecream import ic

class ChessGame:
    def __init__(self) -> None:
        pass

    def run(self):
        GAME_CONFIG.reset_clock()
        run = True
        gs = GameState()
        valid_moves = gs.get_valid_moves()
        sq_selected = ()
        player_clicks = []
        move_made = False
        suspend_moving = False
        game_over = False

        while run:
            player_turn = (gs.white_to_move and GAME_CONFIG.PLAYER_WHITE) or (not gs.white_to_move and GAME_CONFIG.PLAYER_BLACK)
            GAME_CONFIG.CLOCK.tick(GAME_CONFIG.FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                
                # MOUSE CLICKS
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    location = pygame.mouse.get_pos()
                    col = location[0] // GAME_CONFIG.TILE_WIDTH
                    row = location[1] // GAME_CONFIG.TILE_WIDTH
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
                                do_animation = True
                                sq_selected = ()
                                player_clicks = []
                        
                        if not move_made:
                            player_clicks = [sq_selected]
                
                # KEYBOARD PRESSES
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_z:
                        
                        gs.undo_move()
                        if not (GAME_CONFIG.PLAYER_WHITE and GAME_CONFIG.PLAYER_BLACK):
                            gs.undo_move() # extra undo if computer player
                        move_made = True
                        do_animation = False
                        suspend_moving = True
                        print('Undo_pressed')

                    elif event.key == pygame.K_r:
                        GAME_CONFIG.reset_clock()
                        run = True
                        gs = GameState()
                        valid_moves = gs.get_valid_moves()
                        sq_selected = ()
                        player_clicks = []
                        move_made = False
                        suspend_moving = True
            
            # AI MOVE FINDER
            if not suspend_moving and not game_over and not player_turn:
                random_ai = RandomAI(gs)
                # ai_move = find_greedy_move(gs, valid_moves)
                ai_move = None
                if not ai_move:
                    ai_move = random_ai.find_random_move()
                gs.make_move(ai_move)
                move_made = True

            # ANIMATE MOVE
            if move_made:
                if do_animation and GAME_CONFIG.ANIMATE:
                    self._animate_moves(gs.move_log[-1], gs.board)
                valid_moves = gs.get_valid_moves()
                move_made = False
                suspend_moving = False

            
            self._draw_gamestate(gs, valid_moves, sq_selected)

            if gs.checkmate:
                game_over = True
                if gs.white_to_move:
                    self._draw_text('CHECKMATE. Black wins!')
                else:
                    self._draw_text('CHECKMATE. White wins!')
            elif gs.stalemate:
                game_over = True
                self._draw_text('Stalemate.')



            pygame.display.flip()
        pygame.quit()

    def _draw_gamestate(self, gs, valid_moves, sq_selected):
        self._draw_board()
        self._draw_pieces(gs.board)
        self._draw_square_highlights(gs, valid_moves, sq_selected)

    def _draw_board(self):
        for row in range(GAME_CONFIG.DIMENSION):
            for col in range(GAME_CONFIG.DIMENSION):
                squareColour = GAME_CONFIG.LIGHT if ((col + row) % 2 == 0) else GAME_CONFIG.DARK
                pygame.draw.rect(GAME_CONFIG.WIN, squareColour, pygame.Rect(col*GAME_CONFIG.TILE_WIDTH, row*GAME_CONFIG.TILE_WIDTH, GAME_CONFIG.TILE_WIDTH, GAME_CONFIG.TILE_WIDTH))

    def _draw_pieces(self, board):
        for rank in range(GAME_CONFIG.DIMENSION):
            for file in range(GAME_CONFIG.DIMENSION):
                piece = board[rank][file]
                if piece != '--':
                    GAME_CONFIG.WIN.blit(GAME_CONFIG.IMAGES[piece], pygame.Rect(file*GAME_CONFIG.TILE_WIDTH, rank*GAME_CONFIG.TILE_WIDTH, GAME_CONFIG.TILE_WIDTH, GAME_CONFIG.TILE_WIDTH))    

    def _draw_square_highlights(self, gs, valid_moves, sq_selected):
        if sq_selected != ():
            r,c = sq_selected
            if gs.board[r][c][0] == ('w' if gs.white_to_move else 'b'):
                sq = pygame.Surface((GAME_CONFIG.TILE_WIDTH, GAME_CONFIG.TILE_WIDTH))
                sq.set_alpha(98)
                sq.fill('#f28095')
                GAME_CONFIG.WIN.blit(sq, (c * GAME_CONFIG.TILE_WIDTH, r * GAME_CONFIG.TILE_WIDTH))
                sq.fill('#f2b380')
                for move in valid_moves:
                    if move.start_row == r and move.start_col == c:
                        GAME_CONFIG.WIN.blit(sq, (move.end_col * GAME_CONFIG.TILE_WIDTH, move.end_row * GAME_CONFIG.TILE_WIDTH))

    def _draw_text(self, text):
        pygame.font.init()
        font = pygame.font.SysFont("arial", 32, True, False)
        text_object = font.render(text, 0, pygame.Color('slategrey'))
        text_location = pygame.Rect(0,0, GAME_CONFIG.BOARD_WIDTH, GAME_CONFIG.BOARD_WIDTH).move(GAME_CONFIG.BOARD_WIDTH/2 - text_object.get_width()/2, GAME_CONFIG.BOARD_WIDTH/2 - text_object.get_height()/2)
        GAME_CONFIG.WIN.blit(text_object, text_location)
        text_object = font.render(text, 0, pygame.Color('blue4'))
        GAME_CONFIG.WIN.blit(text_object, text_location.move(-1,-1))

    def _animate_moves(self, move, board):
        dr = move.end_row - move.start_row
        dc = move.end_col - move.start_col
        frames_per_sq = 3
        frame_count = (abs(dr) + abs(dc)) * frames_per_sq
        for frame in range(frame_count + 1):
            r,c = (move.start_row + dr * frame / frame_count,move.start_col + dc * frame / frame_count)
            self._draw_board()
            self._draw_pieces(board)
            colour = GAME_CONFIG.LIGHT if ((move.end_col + move.end_row) % 2 == 0) else GAME_CONFIG.DARK
            end_square = pygame.Rect(move.end_col * GAME_CONFIG.TILE_WIDTH, move.end_row * GAME_CONFIG.TILE_WIDTH, GAME_CONFIG.TILE_WIDTH, GAME_CONFIG.TILE_WIDTH)
            pygame.draw.rect(GAME_CONFIG.WIN,colour, end_square)

            # draw captured piece
            if move.piece_captured != '--':
                if move.is_en_passant:
                    en_passant_row = (move.end_row - 1) if move.piece_moved[0] == 'b' else (move.end_row + 1)
                    end_square = pygame.Rect(move.end_col * GAME_CONFIG.TILE_WIDTH, en_passant_row * GAME_CONFIG.TILE_WIDTH, GAME_CONFIG.TILE_WIDTH, GAME_CONFIG.TILE_WIDTH)
                GAME_CONFIG.WIN.blit(GAME_CONFIG.IMAGES[move.piece_captured], end_square)

            # draw moving piece
            if move.piece_moved != '--':
                GAME_CONFIG.WIN.blit(GAME_CONFIG.IMAGES[move.piece_moved], pygame.Rect(c * GAME_CONFIG.TILE_WIDTH, r * GAME_CONFIG.TILE_WIDTH, GAME_CONFIG.TILE_WIDTH, GAME_CONFIG.TILE_WIDTH))
            pygame.display.flip()
            GAME_CONFIG.CLOCK.tick(60)



    