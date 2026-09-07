#----------------------------------------------------------------------------------#
# Minimax AI for Connect 4.

# This file is responsible for choosing the yellow player's moves. 
# Minimax simulates possible AI and human moves without changing the real game board.
# The search is limited to four moves ahead, after which a heuristic function
# estimates which board position is better for the AI.
#
# After adding Alpha-Beta Pruning the search limit can be increased,
# but for now it's 4 to maintain efficient speed and inteligence at the same time
#----------------------------------------------------------------------------------#

# The values must match the constants used in app.py.
ROWS = 6
COLS = 7
EMPTY = 0
RED = 1
YELLOW = 2

# Searching the complete Connect 4 game tree would take too long. Therefore,
# the AI searches four moves (DEPTH = 4) ahead and then evaluates the resulting position.
# Without pruning depth 8 takes about 12 seconds (Lvl 100 mafia boss)
# With pruning about 1 second
DEPTH = 8

def get_valid_moves(board):
    """Return a list containing every column that still has an empty space."""
    valid_moves = []

    for col in range(COLS):
        if board[0][col] == EMPTY:
            valid_moves.append(col)

    return valid_moves

def make_move(board, col, player):
    #-----------------------------------------------------------------------#
    # Create a simulated move on a copy of the board.

    # Minimax must not modify the real game board while testing future moves.
    # A copy is created first, and the token is placed in its lowest empty row.
    #-----------------------------------------------------------------------#
    
    new_board = [row[:] for row in board]

    for row in range(ROWS - 1, -1, -1):
        if new_board[row][col] == EMPTY:
            new_board[row][col] = player
            return new_board, row

    return new_board, None

def check_winner(board, row, col, player):
    """Check whether the token just placed at (row, col) completed four in a row."""
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]

    for dr, dc in directions:
        count = 1

        for step in range(1, 4):
            r = row + dr * step
            c = col + dc * step
            if r < 0 or r >= ROWS or c < 0 or c >= COLS:
                break
            if board[r][c] == player:
                count += 1
            else:
                break

        for step in range(1, 4):
            r = row - dr * step
            c = col - dc * step
            if r < 0 or r >= ROWS or c < 0 or c >= COLS:
                break
            if board[r][c] == player:
                count += 1
            else:
                break

        if count >= 4:
            return True

def evaluate_window(window):
    #-----------------------------------------------------------------------#
    # Give a heuristic score to one group of four board positions.

    # Positive points represent a good position for the yellow AI. Negative
    # points represent a dangerous position where the red player may win.
    #-----------------------------------------------------------------------#
    score = 0
    ai_tokens = window.count(YELLOW)
    player_tokens = window.count(RED)
    empty_spaces = window.count(EMPTY)

    # Reward groups that help the AI build four connected tokens.
    if ai_tokens == 4:
        score += 100000
    elif ai_tokens == 3 and empty_spaces == 1:
        score += 100
    elif ai_tokens == 2 and empty_spaces == 2:
        score += 10

    # Penalize groups that allow the human player to build a winning line.
    if player_tokens == 4:
        score -= 100000
    elif player_tokens == 3 and empty_spaces == 1:
        score -= 120
    elif player_tokens == 2 and empty_spaces == 2:
        score -= 10

    return score

def evaluate_board(board):
    #-----------------------------------------------------------------------#
    # Calculate the total heuristic score of a board position.
    #
    # The function evaluates the center column and every possible horizontal,
    # vertical and diagonal group of four positions.
    #-----------------------------------------------------------------------#
    score = 0

    # The center is useful because it belongs to more possible winning lines.
    center_tokens = 0
    for row in range(ROWS):
        if board[row][COLS // 2] == YELLOW:
            center_tokens += 1
    score += center_tokens * 6

    # Horizontal groups of four
    for row in range(ROWS):
        for col in range(COLS - 3):
            window = board[row][col:col + 4]
            score += evaluate_window(window)

    # Vertical groups of four
    for col in range(COLS):
        for row in range(ROWS - 3):
            window = []
            for i in range(4):
                window.append(board[row + i][col])
            score += evaluate_window(window)

    # Diagonal down-right groups of four
    for row in range(ROWS - 3):
        for col in range(COLS - 3):
            window = []
            for i in range(4):
                window.append(board[row + i][col + i])
            score += evaluate_window(window)

    # Diagonal up-right groups of four
    for row in range(3, ROWS):
        for col in range(COLS - 3):
            window = []
            for i in range(4):
                window.append(board[row - i][col + i])
            score += evaluate_window(window)

    return score

def minimax(board, depth, maximizing_player, alpha=float('-inf'), beta=float('inf'), last_row=None, last_col=None):
    valid_moves = get_valid_moves(board)
    #-----------------------------------------------------------------------#
    # Search future moves and return the best column and its score.
    # When maximizing_player is True, the yellow AI selects the highest score.
    # When it is False, Minimax assumes that the red player selects the lowest
    # score, meaning the best possible counter-move against the AI.
    #-----------------------------------------------------------------------#
    if last_row is not None:
        if maximizing_player:
            last_player = RED
        else:
            last_player = YELLOW
            
        if check_winner(board, last_row, last_col, last_player):
            if last_player == YELLOW:
                return None, 1000000 + depth
            else:
                return None, -1000000 - depth

    # No moves left = draw
    if len(valid_moves) == 0:
        return None, 0
    # If the depth limit is reached, use the heuristic instead of searching
    # the complete game all the way to the end.
    if depth == 0:
        return None, evaluate_board(board)

    if maximizing_player:
        # AI turn: choose the move with the highest score.
        best_score = float('-inf')
        best_col = valid_moves[0]

        for col in valid_moves:
            new_board, row = make_move(board, col, YELLOW)
            new_score = minimax(new_board, depth - 1, False, alpha, beta, row, col)[1]
            if new_score > best_score:
                best_score = new_score
                best_col = col

            # Alpha is the best score Yellow guarantees
            alpha = max(alpha, best_score)
            # Red has a better option = prune
            if alpha >= beta: break

        return best_col, best_score

    else:
        # Human turn: assume the human chooses the lowest score for the AI.
        best_score = float('inf')
        best_col = valid_moves[0]

        for col in valid_moves:
            new_board, row = make_move(board, col, RED)
            new_score = minimax(new_board, depth - 1, True, alpha, beta, row, col)[1]

            if new_score < best_score:
                best_score = new_score
                best_col = col

            # Beta is the best score Red guarantees
            beta = min(beta, best_score)
            # Yellow has a better option = prune
            if alpha >= beta: break

        return best_col, best_score

def get_best_move(board, depth=DEPTH):
    valid_moves = get_valid_moves(board)
    ai_move_scores = [0] * len(valid_moves)

    alpha = float('-inf')
    beta = float('inf')

    for i, col in enumerate(valid_moves):
        new_board, row = make_move(board, col, YELLOW)
        score = minimax(new_board, depth - 1, False, alpha, beta, row, col)[1]
        ai_move_scores[i] = score

        # Update after evaluation
        alpha = max(alpha, score)

    best_i = ai_move_scores.index(max(ai_move_scores))
    best_col = valid_moves[best_i]

    return best_col, ai_move_scores, valid_moves