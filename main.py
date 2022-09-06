import fen
import pygame
import chess_engine


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
    IMAGES[piece] = pygame.image.load('assets/' + piece + '.png')


def draw_gamestate(WIN, board):
    draw_board(WIN)
    draw_pieces(WIN, board)

def draw_board(WIN):
    for rank in range(DIMENSION):
        for file in range(DIMENSION):
            isLightSquare = ((file + rank) % 2 == 0)
            squareColour = LIGHT if isLightSquare else DARK
            pygame.draw.rect(WIN, squareColour, pygame.Rect(file*TILE_WIDTH, rank*TILE_WIDTH, TILE_WIDTH, TILE_WIDTH))

def draw_pieces(WIN, board):
    for rank in range(DIMENSION):
        for file in range(DIMENSION):
            piece = board[rank][file]
            if piece != '--':
                WIN.blit(IMAGES[piece], pygame.Rect(file*TILE_WIDTH, rank*TILE_WIDTH, TILE_WIDTH, TILE_WIDTH))

def main():
    clock = pygame.time.Clock()
    run = True
    gs = chess_engine.GameState()
    valid_moves = gs.get_valid_moves()
    
    sq_selected = ()
    player_clicks = []
    move_made = False

    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                location = pygame.mouse.get_pos()
                col = location[0] // TILE_WIDTH
                row = location[1] // TILE_WIDTH
                
                if sq_selected == (row, col): # If same square was selected, reset
                    sq_selected = ()
                    player_clicks = []
                else: # If another square
                    sq_selected = (row, col)
                    player_clicks.append(sq_selected)
                
                if len(player_clicks) == 0:
                    print('Selection cleared')

                elif len(player_clicks) == 1:
                    print('Selected')

                elif len(player_clicks) == 2: # Second click submitted
                    move = chess_engine.Move(player_clicks[0], player_clicks[1], gs.board)
                    
                    if move in valid_moves:
                        gs.make_move(move)
                        move_made = True
                    sq_selected = ()
                    player_clicks = []
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:
                    gs.undo_move()
                    move_made = True
        
        if move_made:
            valid_moves = gs.get_valid_moves()
            print('moves reset')
            move_made = False
        
        draw_gamestate(WIN, gs.board)
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()
