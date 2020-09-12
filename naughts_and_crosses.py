import pygame


# Sizes
WINDOW_WIDTH = 600
LINE_WIDTH = 10
LINE1_POS = WINDOW_WIDTH / 3
LINE2_POS = LINE1_POS * 2
# Box sizes
BOX_WIDTH = WINDOW_WIDTH // 3
BOX_RADIUS = BOX_WIDTH / 4

# Colors
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)

# Grid
grid = [0, 0, 0,
        0, 0, 0,
        0, 0, 0]
grid_win_coords = [(0,3,6), (1,4,7), (2,5,8), # vertical wins
                   (0,1,2), (3,4,5), (6,7,8), # horizontal wins
                   (0, 4, 8), (2, 4, 6)]      # diagonal wins
X = 'X'
O = 'O'

# Graphics
pygame.font.init()
font = pygame.font.SysFont('Comic Sans MS', 90)

def init_screen():
    screen = pygame.display.set_mode([WINDOW_WIDTH, WINDOW_WIDTH])
    
    # White background
    screen.fill(COLOR_WHITE)

    # Draw bounding lines
    pygame.draw.line(screen,
                     COLOR_BLACK,
                     (LINE1_POS, 0),
                     (LINE1_POS, WINDOW_WIDTH),
                     LINE_WIDTH)
    pygame.draw.line(screen,
                     COLOR_BLACK,
                     (LINE2_POS, 0),
                     (LINE2_POS, WINDOW_WIDTH),
                     LINE_WIDTH)
    pygame.draw.line(screen,
                     COLOR_BLACK,
                     (0, LINE1_POS),
                     (WINDOW_WIDTH, LINE1_POS),
                     LINE_WIDTH)
    pygame.draw.line(screen,
                     COLOR_BLACK,
                     (0, LINE2_POS),
                     (WINDOW_WIDTH, LINE2_POS),
                     LINE_WIDTH)
    return screen


def get_cell_position(event):
    # grab coords of click
    x, y = event.pos

    # Check dist to dead-zone i.e ambiguous location
    x_dist = min(abs(LINE1_POS-x), abs(LINE2_POS-x))
    y_dist = min(abs(LINE1_POS-y), abs(LINE2_POS-y))
    tolerance = LINE_WIDTH / 2
    if x_dist <= tolerance or y_dist <= tolerance:
        # too close to the lines to make a call
        return None

    # Cell position
    x_idx = x // BOX_WIDTH
    y_idx = y // BOX_WIDTH
    return (y_idx * 3) + x_idx


def do_player_turn(screen, cell, icon):
    # Can't overwrite anything
    if grid[cell]:
        return False

    grid[cell] = icon
    # Get center of box coords
    x_idx = cell % 3
    y_idx = cell // 3
    x_pos = (x_idx * BOX_WIDTH) + BOX_RADIUS
    y_pos = (y_idx * BOX_WIDTH) + BOX_RADIUS

    # Paint cell
    icon_surface = font.render(icon, False, COLOR_BLACK)
    screen.blit(icon_surface, (x_pos, y_pos))
    return True


def game_winner():
    for grid_win_coord in grid_win_coords:
        idx_1, idx_2, idx_3 = grid_win_coord
        if grid[idx_1] and grid[idx_1] == grid[idx_2] == grid[idx_3]:
            return grid[idx_1]
    return None


def remaining_movies_possible():
    return 0 in grid


def minimax(o_last_move, best_move_dict):
    # check for winner and return score
    # Evaluation function is:
    #   1 + no. free squares for O win
    #  -(1 + no. free squares) for X win
    #   0 for draw
    winner = game_winner()
    if winner:
        score = 1 + sum(1 for x in grid if x == 0)
        return score if o_last_move else -score

    # No winner but no more moves, its a draw
    if not remaining_movies_possible():
        return 0

    # Try every remaining possibility
    best_move_val = 100 if o_last_move else -100
    best_move_cell = -1
    for i, cell in enumerate(grid):
        if cell != 0:
            continue
        
        # update grid in place and use recursivley
        grid[i] = X if o_last_move else O
        val = minimax(not o_last_move, best_move_dict)
        if o_last_move:
            # this means this is X's move, so we want to minimize
            best_move_val = min(val, best_move_val)
        else:
            best_move_val = max(val, best_move_val)
        # update our pointer in case a better score was found
        best_move_cell = i if best_move_val == val else best_move_cell
        grid[i] = 0

    # pass-by-reference return item
    best_move_dict[0] = best_move_cell
    return best_move_val

def process_turn(screen, event):
    # OPnly consider first mouse button 
    if event.button != 1:
        return

    # Check if valid user turn
    cell = get_cell_position(event)
    if cell is None:
        return

    # Add user turn
    is_ai_turn = do_player_turn(screen, cell, X)
    # AI turn
    if is_ai_turn:
        # Check if anyone won yet?
        winner = game_winner()
        if winner:
            print('Winner is %s' % winner)
            return
        if not remaining_movies_possible():
            print('Round Draw')
            return

        # Call minimax function, do turn
        r = {0: -1}
        minimax(False, r)
        do_player_turn(screen, r[0], O)

        # Check if anyone won yet?
        winner = game_winner()
        if winner:
            print('Winner is %s' % winner)
            return
        if not remaining_movies_possible():
            print('Round Draw')
            return


def main():
    pygame.init()
    screen = init_screen()
    while True:
        # Check for clean exit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                process_turn(screen, event)
        pygame.display.flip()

if __name__ == '__main__':
    main()