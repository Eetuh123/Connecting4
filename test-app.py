from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

# Imports the function that asks the Minimax algorithm to choose an AI move.
from ai import get_best_move

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
CORS(app)

# Game constants
ROWS = 6
COLS = 7
EMPTY = 0
RED = 1
YELLOW = 2

# SMARTer makes look further in future but very slow can be like 5.7 million search things
DIFFICULTIES = {
    'easy': 2,
    'medium': 4,
    'hard': 6
}

# Game state (in-memory for simplicity)
game_state = {
    'board': [[EMPTY for _ in range(COLS)] for _ in range(ROWS)],
    'current_player': RED,
    'game_over': False,
    'winner': None,
    'move_count': 0,
    'difficulty': 'medium',
    'ai_move_scores': [],
    'valid_moves': []
}

def reset_game():
    """Reset the game state"""
    game_state['board'] = [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]
    game_state['current_player'] = RED
    game_state['game_over'] = False
    game_state['winner'] = None
    game_state['move_count'] = 0
    game_state['ai_move_scores'] = []
    game_state['valid_moves'] = []

def is_board_full():
    """Check if the board is full"""
    for c in range(COLS):
        if game_state['board'][0][c] == EMPTY:
            return False
    return True

def check_win(row, col, player):
    """Check if the current move results in a win"""
    if player == EMPTY:
        return False
    
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
    
    for dr, dc in directions:
        count = 1
        
        # Check positive direction
        for step in range(1, 4):
            r = row + dr * step
            c = col + dc * step
            if r < 0 or r >= ROWS or c < 0 or c >= COLS:
                break
            if game_state['board'][r][c] == player:
                count += 1
            else:
                break
        
        # Check negative direction
        for step in range(1, 4):
            r = row - dr * step
            c = col - dc * step
            if r < 0 or r >= ROWS or c < 0 or c >= COLS:
                break
            if game_state['board'][r][c] == player:
                count += 1
            else:
                break
        
        if count >= 4:
            return True
    return False

@app.route('/')
def index():
    """Serve the main game page"""
    return render_template('index.html')

@app.route('/api/reset', methods=['POST'])
def reset():
    """Reset the game"""
    reset_game()
    return jsonify({
        'success': True,
        'board': game_state['board'],
        'current_player': game_state['current_player'],
        'game_over': game_state['game_over'],
        'winner': game_state['winner'],
        'difficulty': game_state['difficulty'],
        'ai_move_scores': game_state['ai_move_scores'],
        'valid_moves': game_state['valid_moves']
    })

@app.route('/api/difficulty', methods=['POST'])
def set_difficulty():
    """Make Ai SMARTer"""
    data = request.get_json()
    level = data.get('level')

    if level not in DIFFICULTIES:
        return jsonify({'error': 'Invalid difficulty level'}), 400

    game_state['difficulty'] = level
    return jsonify({'success': True, 'difficulty': level})

@app.route('/api/move', methods=['POST'])
def make_move():
    """Make a move in the game"""
    data = request.get_json()
    col = data.get('col')
    
    if col is None or col < 0 or col >= COLS:
        return jsonify({'error': 'Invalid column'}), 400
    
    if game_state['game_over']:
        return jsonify({'error': 'Game is over'}), 400
    
    if game_state['board'][0][col] != EMPTY:
        return jsonify({'error': 'Column is full'}), 400
    
    # Find the lowest empty row
    row = -1
    for r in range(ROWS - 1, -1, -1):
        if game_state['board'][r][col] == EMPTY:
            row = r
            break
    
    if row == -1:
        return jsonify({'error': 'Column is full'}), 400
    
    # Place the token
    player = game_state['current_player']
    game_state['board'][row][col] = player
    game_state['move_count'] += 1
    
    # Check for win
    if check_win(row, col, player):
        game_state['game_over'] = True
        game_state['winner'] = player
    elif is_board_full():
        game_state['game_over'] = True
        game_state['winner'] = 0  # Draw
    
    # Switch player
    if not game_state['game_over']:
        game_state['current_player'] = YELLOW if player == RED else RED

    # AI MOVE
    # After the human move, current_player is YELLOW. The board is sent to
    # get_best_move(), which uses Minimax to select a column for the AI.
    if not game_state['game_over'] and game_state['current_player'] == YELLOW:
        depth = DIFFICULTIES[game_state['difficulty']]
        ai_col, ai_move_scores, valid_moves = get_best_move(game_state['board'], depth)
        game_state['ai_move_scores'] = ai_move_scores
        game_state['valid_moves'] = valid_moves

        if ai_col is not None:
            # Find the lowest empty row in the column selected by Minimax.
            ai_row = -1
            for r in range(ROWS - 1, -1, -1):
                if game_state['board'][r][ai_col] == EMPTY:
                    ai_row = r
                    break

            # Place the yellow AI token on the real game board.
            game_state['board'][ai_row][ai_col] = YELLOW
            game_state['move_count'] += 1

            # Check whether the AI move ended the game.
            if check_win(ai_row, ai_col, YELLOW):
                game_state['game_over'] = True
                game_state['winner'] = YELLOW
            elif is_board_full():
                game_state['game_over'] = True
                game_state['winner'] = 0  # Draw

            # If the game continues, the next API request will be a human move.
            if not game_state['game_over']:
                game_state['current_player'] = RED
    
    return jsonify({
        'success': True,
        'row': row,
        'col': col,
        'player': player,
        'board': game_state['board'],
        'current_player': game_state['current_player'],
        'game_over': game_state['game_over'],
        'winner': game_state['winner'],
        'move_count': game_state['move_count'],
        'ai_move_scores': game_state['ai_move_scores'],
        'valid_moves': game_state['valid_moves'],
        'difficulty': game_state['difficulty']
    })

@app.route('/api/state', methods=['GET'])
def get_state():
    """Get the current game state"""
    return jsonify({
        'board': game_state['board'],
        'current_player': game_state['current_player'],
        'game_over': game_state['game_over'],
        'winner': game_state['winner'],
        'move_count': game_state['move_count'],
        'difficulty': game_state['difficulty']
    })

if __name__ == '__main__':
    import os

    reset_game()
    port = int(os.environ.get('PORT', 5000))

    try:
        # In development, serve through livereload so the browser
        # auto-refreshes whenever a template or static asset changes.
        # Werkzeug's reloader (not livereload's own tornado.autoreload,
        # which is unreliable on Windows) restarts the process on .py changes.
        from livereload import Server
        try:
            from werkzeug.serving import run_with_reloader
        except ImportError:
            # Newer Werkzeug moved this to a private module.
            from werkzeug._reloader import run_with_reloader

        def _serve():
            server = Server(app.wsgi_app)
            server.watch('templates/*.html')
            server.watch('static/*.css')
            server.watch('static/*.js')
            server.serve(port=port, host='127.0.0.1', debug=False)

        run_with_reloader(_serve)
    except ImportError:
        app.run(debug=True, port=port)
