// Game state
let board = [];
let currentPlayer = 1; // 1 = Red, 2 = Yellow
let gameOver = false;
let moveCount = 0;
let hoveredColumn = null;
let moveInProgress = false; // Prevent extra clicks while the AI is thinking

// DOM elements
const boardEl = document.getElementById('board');
const turnText = document.getElementById('turnText');
const turnDot = document.getElementById('turnDot');
const resetBtn = document.getElementById('resetBtn');
const moveCounter = document.getElementById('moveCounter');
const diffButtons = document.querySelectorAll('.diff-choice');

// API base URL
const API_URL = window.location.origin;

// Helper to convert cell value to class
function getCellClass(val) {
    if (val === 1) return 'red';
    if (val === 2) return 'yellow';
    return '';
}

// Render board
function renderBoard(boardData, aiMoveScores = null, validMoves = null, aiMove = null) {
    const boardEl = document.getElementById('board');
    boardEl.innerHTML = '';
    const scoreByCol = {};
    if (aiMoveScores && validMoves) {
        validMoves.forEach((col, i) => {
            scoreByCol[col] = aiMoveScores[i];
        });
    }

    for (let c = 0; c < 7; c++) {
        const column = document.createElement('div');
        column.className = 'column';
        column.dataset.col = c;

        let scoreRow;
        if (aiMove && aiMove.col === c) {
            scoreRow = aiMove.row;
        } else {
            scoreRow = -1;
            for (let r = 5; r >= 0; r--) {
                if (boardData[r][c] === 0) {
                    scoreRow = r;
                    break;
                }
            }
        }

        for (let r = 5; r >= 0; r--) {
            const cell = document.createElement('div');
            cell.className = 'cell';
            cell.dataset.row = r;
            cell.dataset.col = c;

            if (boardData[r][c] === 1) cell.classList.add('red');
            if (boardData[r][c] === 2) cell.classList.add('yellow');

            if (r === scoreRow && scoreByCol[c] !== undefined) {
                const score = scoreByCol[c];
                cell.dataset.score = score;
                cell.title = `AI Score: ${score}`;

                const scoreLabel = document.createElement('span');
                scoreLabel.className = 'score-label';
                scoreLabel.textContent = score;
                cell.appendChild(scoreLabel);
            }

            column.appendChild(cell);
        }

        boardEl.appendChild(column);
    }

    setupHoverEvents();
    updateGameOverState(); // Update game over styling
}

// Game over
function updateGameOverState() {
    const board = document.getElementById('board');
    const boardWrapper = document.querySelector('.board-wrapper');
    
    if (gameOver) {
        board.classList.add('game-over');
        boardWrapper.classList.add('game-over');
    } else {
        board.classList.remove('game-over');
        boardWrapper.classList.remove('game-over');
    }
}

// Preview token
function setupHoverEvents() {
    const columns = document.querySelectorAll('.column');
    
    columns.forEach(column => {
        const newColumn = column.cloneNode(true);
        column.parentNode.replaceChild(newColumn, column);
    });
    
    document.querySelectorAll('.column').forEach(column => {
        column.addEventListener('mouseenter', function(e) {
            if (gameOver || moveInProgress) return;
            const col = parseInt(this.dataset.col);
            showPreview(col);
        });
        
        column.addEventListener('mouseleave', function(e) {
            clearPreview();
        });
    });
}

function showPreview(col) {
    // No preview if the game is over or the AI is thinking
    if (gameOver || moveInProgress) return;
    
    clearPreview();
    
    const cells = document.querySelectorAll(`.column[data-col="${col}"] .cell`);
    const cellArray = Array.from(cells);
    
    let bottomEmptyIndex = -1;
    for (let i = cellArray.length - 1; i >= 0; i--) {
        const cell = cellArray[i];
        if (!cell.classList.contains('red') && !cell.classList.contains('yellow')) {
            bottomEmptyIndex = i;
            break;
        }
    }
    
    if (bottomEmptyIndex === -1) return;
    hoveredColumn = col;
    
    const previewCell = cellArray[bottomEmptyIndex];
    const previewClass = currentPlayer === 1 ? 'preview-red' : 'preview-yellow';
    previewCell.classList.add(previewClass);
    
    const column = document.querySelector(`.column[data-col="${col}"]`);
    if (column) { column.classList.add('column-hover'); }
}

function clearPreview() {
    document.querySelectorAll('.preview-red, .preview-yellow').forEach(cell => {
        cell.classList.remove('preview-red', 'preview-yellow');
    });
    
    document.querySelectorAll('.column-hover').forEach(column => {
        column.classList.remove('column-hover');
    });
    
    hoveredColumn = null;
}

// Update the turn indicator
function updateTurnIndicator(state) {
    const { current_player, game_over, winner } = state;
    
    // Update game over state
    gameOver = game_over;
    updateGameOverState();
    
    if (game_over) {
        if (winner === 1) {
            turnText.textContent = '🏆 Red Wins!';
            turnDot.className = 'dot red';
        } else if (winner === 2) {
            turnText.textContent = '🏆 Yellow Wins!';
            turnDot.className = 'dot yellow';
        } else if (winner === 0) {
            turnText.textContent = '🤝 Draw!';
            turnDot.className = 'dot empty';
        } else {
            turnText.textContent = 'Game Over';
            turnDot.className = 'dot empty';
        }
        return;
    }

    if (current_player === 1) {
        turnText.textContent = "Red's turn";
        turnDot.className = 'dot red';
    } else {
        turnText.textContent = "Yellow's turn";
        turnDot.className = 'dot yellow';
    }
}

// Update move counter
function updateMoveCounter(count) { moveCounter.textContent = `Move ${count}`; }

// Dificulty button highlight
function updateDifficultyButtons(level) {
    diffButtons.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.level === level);
    });
}

// Make Ai SMARTer
function setDifficulty(level) {
    if (moveInProgress) return;

    fetch(`${API_URL}/api/difficulty`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ level: level })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
            return;
        }
        updateDifficultyButtons(data.difficulty);
    })
    .catch(error => {
        console.error('Error setting difficulty:', error);
    });
}

// Load game state from server
function loadGameState() {
    fetch(`${API_URL}/api/state`)
        .then(response => response.json())
        .then(data => {
            board = data.board;
            currentPlayer = data.current_player;
            gameOver = data.game_over;
            moveCount = data.move_count;
            renderBoard(board);
            updateTurnIndicator(data);
            updateMoveCounter(data.move_count);
            updateDifficultyButtons(data.difficulty);
            setupHoverEvents();
            updateGameOverState();
        })
        .catch(error => {
            console.error('Error loading game state:', error);
            turnText.textContent = '⚠️ Connection Error';
        });
}

// Make a move
function makeMove(col) {
    if (gameOver || moveInProgress) return;

    // Lock the board while the human move is submitted and rendered
    moveInProgress = true;
    resetBtn.disabled = true;
    diffButtons.forEach(btn => { btn.disabled = true; });
    clearPreview();

    fetch(`${API_URL}/api/move`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ col: col })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
            unlockBoard();
            return;
        }
        board = data.board;
        currentPlayer = data.current_player;
        gameOver = data.game_over;
        moveCount = data.move_count;

        // Show the human's piece before the AI takes its turn
        renderBoard(board);
        updateTurnIndicator(data);
        updateMoveCounter(data.move_count);
        setupHoverEvents();
        updateGameOverState();

        if (!gameOver && currentPlayer === 2) {
            turnText.textContent = 'AI is thinking...';
            turnDot.className = 'dot yellow';
            requestAiMove();
        } else {
            unlockBoard();
        }
    })
    .catch(error => {
        console.error('Error making move:', error);
        alert('Failed to make move. Please try again.');
        unlockBoard();
    });
}

// Ask the server for the AI's move, once the human move is already on screen
function requestAiMove() {
    fetch(`${API_URL}/api/ai-move`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
            return;
        }
        board = data.board;
        currentPlayer = data.current_player;
        gameOver = data.game_over;
        moveCount = data.move_count;
        renderBoard(board, data.ai_move_scores, data.valid_moves, { row: data.row, col: data.col });
        updateTurnIndicator(data);
        updateMoveCounter(data.move_count);
        clearPreview();
        setupHoverEvents();
        updateGameOverState();
    })
    .catch(error => {
        console.error('Error getting AI move:', error);
        alert('Failed to get AI move. Please try again.');
    })
    .finally(() => {
        unlockBoard();
    });
}

// Re-enable input after a full turn (human + AI) is complete
function unlockBoard() {
    moveInProgress = false;
    resetBtn.disabled = false;
    diffButtons.forEach(btn => { btn.disabled = false; });

    if (!gameOver) {
        turnText.textContent = "Red's turn";
        turnDot.className = 'dot red';
    }
}

// Reset the game
function resetGame() {
    if (moveInProgress) return;

    fetch(`${API_URL}/api/reset`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        board = data.board;
        currentPlayer = data.current_player;
        gameOver = data.game_over;
        moveCount = 0;
        renderBoard(board);
        updateTurnIndicator(data);
        updateMoveCounter(0);
        updateDifficultyButtons(data.difficulty);
        clearPreview();
        setupHoverEvents();
        updateGameOverState();
    })
    .catch(error => {
        console.error('Error resetting game:', error);
        alert('Failed to reset game. Please refresh the page.');
    });
}

// Handle click on board
function onBoardClick(e) {
    const cell = e.target.closest('.cell');
    if (!cell) return;
    if (gameOver || moveInProgress) return;
    const col = parseInt(cell.dataset.col, 10);
    if (isNaN(col)) return;
    makeMove(col);
}

// Initialize the game
function init() {
    boardEl.addEventListener('click', onBoardClick);
    resetBtn.addEventListener('click', resetGame);
    diffButtons.forEach(btn => {
        btn.addEventListener('click', () => setDifficulty(btn.dataset.level));
    });
    loadGameState();

    setInterval(() => {
        if (!gameOver && !moveInProgress) {
            fetch(`${API_URL}/api/state`)
                .then(response => response.json())
                .then(data => {
                    if (JSON.stringify(data.board) !== JSON.stringify(board)) {
                        board = data.board;
                        currentPlayer = data.current_player;
                        gameOver = data.game_over;
                        moveCount = data.move_count;
                        renderBoard(board);
                        updateTurnIndicator(data);
                        updateMoveCounter(data.move_count);
                        setupHoverEvents();
                        updateGameOverState();
                    }
                })
                .catch(() => {});
        }
    }, 3000);
}

// Start the game when page loads
document.addEventListener('DOMContentLoaded', init);