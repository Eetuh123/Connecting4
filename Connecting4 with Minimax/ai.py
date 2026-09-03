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
# the AI searches four moves ahead and then evaluates the resulting position.
DEPTH = 4


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
            break

    return new_board


def check_winner(board, player):
    """Check every direction to see if a player has four connected tokens."""
    # Horizontal
    for row in range(ROWS):
        for col in range(COLS - 3):
            if (board[row][col] == player and
                    board[row][col + 1] == player and
                    board[row][col + 2] == player and
                    board[row][col + 3] == player):
                return True

    # Vertical
    for row in range(ROWS - 3):
        for col in range(COLS):
            if (board[row][col] == player and
                    board[row + 1][col] == player and
                    board[row + 2][col] == player and
                    board[row + 3][col] == player):
                return True

    # Diagonal down-right
    for row in range(ROWS - 3):
        for col in range(COLS - 3):
            if (board[row][col] == player and
                    board[row + 1][col + 1] == player and
                    board[row + 2][col + 2] == player and
                    board[row + 3][col + 3] == player):
                return True

    # Diagonal up-right
    for row in range(3, ROWS):
        for col in range(COLS - 3):
            if (board[row][col] == player and
                    board[row - 1][col + 1] == player and
                    board[row - 2][col + 2] == player and
                    board[row - 3][col + 3] == player):
                return True

    return False


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


def minimax(board, depth, maximizing_player):
    #-----------------------------------------------------------------------#
    # Search future moves and return the best column and its score.
    # When maximizing_player is True, the yellow AI selects the highest score.
    # When it is False, Minimax assumes that the red player selects the lowest
    # score, meaning the best possible counter-move against the AI.
    #-----------------------------------------------------------------------#
    
    valid_moves = get_valid_moves(board)
    ai_wins = check_winner(board, YELLOW)
    player_wins = check_winner(board, RED)

    # Terminal positions stop the recursion immediately. An AI win receives a
    # large positive score, while a human win receives a large negative score.
    if ai_wins:
        return None, 1000000
    if player_wins:
        return None, -1000000
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
            new_board = make_move(board, col, YELLOW)
            new_score = minimax(new_board, depth - 1, False)[1]

            if new_score > best_score:
                best_score = new_score
                best_col = col

        return best_col, best_score

    else:
        # Human turn: assume the human chooses the lowest score for the AI.
        best_score = float('inf')
        best_col = valid_moves[0]

        for col in valid_moves:
            new_board = make_move(board, col, RED)
            new_score = minimax(new_board, depth - 1, True)[1]

            if new_score < best_score:
                best_score = new_score
                best_col = col

        return best_col, best_score


def get_best_move(board):
    """Start the Minimax search and return the column selected for the AI."""
    best_col, score = minimax(board, DEPTH, True)
    return best_col
