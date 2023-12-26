import pygame
from app.chess_engine import GameState, Move
from app.chess_ai import find_random_move, find_greedy_move

ASSETS_FOLDER = 'app/assets/'

DIMENSION = 8
TILE_WIDTH = 60
BOARD_WIDTH = TILE_WIDTH * DIMENSION
LIGHT = '#EEEEEE'
DARK = '#48a1d9'

WIN = pygame.display.set_mode((BOARD_WIDTH, BOARD_WIDTH))
CAPTION = 'DL Chess'
FPS = 15
pygame.display.set_caption(CAPTION)

PIECES = ['bB', 'bK', 'bN', 'bP', 'bQ', 'bR', 'wB', 'wK', 'wN', 'wP', 'wQ', 'wR']
IMAGES = {}
for piece in PIECES:
    IMAGES[piece] = pygame.image.load(ASSETS_FOLDER + piece + '.png')


def draw_square_highlights(WIN, gs, valid_moves, sq_selected):
    if sq_selected != ():
        r,c = sq_selected
        if gs.board[r][c][0] == ('w' if gs.white_to_move else 'b'):
            sq = pygame.Surface((TILE_WIDTH, TILE_WIDTH))
            sq.set_alpha(98)
            sq.fill('#f28095')
            WIN.blit(sq, (c * TILE_WIDTH, r * TILE_WIDTH))
            sq.fill('#f2b380')
            for move in valid_moves:
                if move.start_row == r and move.start_col == c:
                    WIN.blit(sq, (move.end_col * TILE_WIDTH, move.end_row * TILE_WIDTH))

def draw_gamestate(WIN, gs, valid_moves, sq_selected):
    draw_board(WIN)
    draw_square_highlights(WIN,gs, valid_moves, sq_selected)
    draw_pieces(WIN, gs.board)

def draw_board(WIN):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            isLightSquare = ((col + row) % 2 == 0)
            squareColour = LIGHT if isLightSquare else DARK
            pygame.draw.rect(WIN, squareColour, pygame.Rect(col*TILE_WIDTH, row*TILE_WIDTH, TILE_WIDTH, TILE_WIDTH))

def draw_pieces(WIN, board):
    for rank in range(DIMENSION):
        for file in range(DIMENSION):
            piece = board[rank][file]
            if piece != '--':
                WIN.blit(IMAGES[piece], pygame.Rect(file*TILE_WIDTH, rank*TILE_WIDTH, TILE_WIDTH, TILE_WIDTH))


def animate_moves(move,WIN,board,clock):
    dr = move.end_row - move.start_row
    dc = move.end_col - move.start_col
    frames_per_sq = 3
    frame_count = (abs(dr) + abs(dc)) * frames_per_sq
    for frame in range(frame_count + 1):
        r,c = (move.start_row + dr * frame / frame_count,move.start_col + dc * frame / frame_count)
        draw_board(WIN)
        draw_pieces(WIN,board)
        colour = LIGHT if ((move.end_col + move.end_row) % 2 == 0) else DARK
        end_square = pygame.Rect(move.end_col * TILE_WIDTH, move.end_row * TILE_WIDTH, TILE_WIDTH, TILE_WIDTH)
        pygame.draw.rect(WIN,colour, end_square)

        # draw captured piece
        if move.piece_captured != '--':
            if move.is_en_passant:
                en_passant_row = (move.end_row - 1) if move.piece_moved[0] == 'b' else (move.end_row + 1)
                end_square = pygame.Rect(move.end_col * TILE_WIDTH, en_passant_row * TILE_WIDTH, TILE_WIDTH, TILE_WIDTH)
            WIN.blit(IMAGES[move.piece_captured], end_square)

        # draw moving piece
        if move.piece_moved != '--':
            WIN.blit(IMAGES[move.piece_moved], pygame.Rect(c * TILE_WIDTH, r * TILE_WIDTH, TILE_WIDTH, TILE_WIDTH))
        pygame.display.flip()
        clock.tick(60)


def draw_text(screen, text):
    pygame.font.init()
    font = pygame.font.SysFont("arial", 32, True, False)
    text_object = font.render(text, 0, pygame.Color('slategrey'))
    text_location = pygame.Rect(0,0, BOARD_WIDTH, BOARD_WIDTH).move(BOARD_WIDTH/2 - text_object.get_width()/2, BOARD_WIDTH/2 - text_object.get_height()/2)
    screen.blit(text_object, text_location)
    text_object = font.render(text, 0, pygame.Color('blue4'))
    screen.blit(text_object, text_location.move(-1,-1))



def run_game():
    clock = pygame.time.Clock()
    run = True
    gs = GameState()
    valid_moves = gs.get_valid_moves()
    sq_selected = ()
    player_clicks = []
    move_made = False
    ANIMATE = True
    game_over = False

    player_white = True
    player_black = False
    
    while run:
        player_turn = (gs.white_to_move and player_white) or (not gs.white_to_move and player_black)
    
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
            # mouse clicks
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not game_over and player_turn:
                    location = pygame.mouse.get_pos()
                    col = location[0] // TILE_WIDTH
                    row = location[1] // TILE_WIDTH
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
                
            # key handlers
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:
                    gs.undo_move()
                    move_made = True
                    ANIMATE = False
                    game_over = False

                elif event.key == pygame.K_r:
                    clock = pygame.time.Clock()
                    run = True
                    gs = GameState()
                    valid_moves = gs.get_valid_moves()
                    sq_selected = ()
                    player_clicks = []
                    move_made = False
                    game_over = False
        

        # AI move finder
        if not game_over and not player_turn:
            ai_move = find_greedy_move(gs, valid_moves)
            if not ai_move:
                ai_move = find_random_move(valid_moves)
            gs.make_move(ai_move)
            move_made = True

        if move_made:
            if ANIMATE:
                animate_moves(gs.move_log[-1], WIN, gs.board, clock)
            valid_moves = gs.get_valid_moves()
            move_made = False
        
        draw_gamestate(WIN, gs, valid_moves, sq_selected)

        if gs.checkmate:
            game_over = True
            if gs.white_to_move:
                draw_text(WIN, 'CHECKMATE. Black wins!')
            else:
                draw_text(WIN, 'CHECKMATE. White wins!')
        elif gs.stalemate:
            game_over = True
            draw_text(WIN, 'Stalemate.')



        pygame.display.flip()
    pygame.quit()