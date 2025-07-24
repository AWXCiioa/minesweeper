class Minesweeper {
    constructor() {
        this.difficulties = {
            easy: { rows: 9, cols: 9, mines: 10 },
            medium: { rows: 16, cols: 16, mines: 40 },
            hard: { rows: 16, cols: 30, mines: 99 }
        };
        
        this.currentDifficulty = 'easy';
        this.board = [];
        this.gameState = 'ready'; // ready, playing, won, lost
        this.timer = 0;
        this.timerInterval = null;
        this.firstClick = true;
        this.flagCount = 0;
        
        this.initializeElements();
        this.setupEventListeners();
        this.resetGame();
    }
    
    initializeElements() {
        this.gameBoard = document.getElementById('game-board');
        this.mineCountElement = document.getElementById('mine-count');
        this.timerElement = document.getElementById('timer');
        this.resetButton = document.getElementById('reset-btn');
        this.gameMessage = document.getElementById('game-message');
        this.difficultyButtons = document.querySelectorAll('.difficulty-btn');
    }
    
    setupEventListeners() {
        this.resetButton.addEventListener('click', () => this.resetGame());
        
        this.difficultyButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.changeDifficulty(e.target.dataset.difficulty);
            });
        });
    }
    
    createBoard() {
        const config = this.difficulties[this.currentDifficulty];
        this.board = [];
        
        for (let row = 0; row < config.rows; row++) {
            this.board[row] = [];
            for (let col = 0; col < config.cols; col++) {
                this.board[row][col] = {
                    isMine: false,
                    isRevealed: false,
                    isFlagged: false,
                    neighborMines: 0
                };
            }
        }
    }
    
    placeMines(excludeRow, excludeCol) {
        const config = this.difficulties[this.currentDifficulty];
        let minesPlaced = 0;
        
        while (minesPlaced < config.mines) {
            const row = Math.floor(Math.random() * config.rows);
            const col = Math.floor(Math.random() * config.cols);
            
            // Don't place mine on first click or if already has mine
            if ((row === excludeRow && col === excludeCol) || this.board[row][col].isMine) {
                continue;
            }
            
            this.board[row][col].isMine = true;
            minesPlaced++;
        }
        
        this.calculateNeighborMines();
    }
    
    calculateNeighborMines() {
        const config = this.difficulties[this.currentDifficulty];
        
        for (let row = 0; row < config.rows; row++) {
            for (let col = 0; col < config.cols; col++) {
                if (!this.board[row][col].isMine) {
                    let count = 0;
                    
                    // Check all 8 neighbors
                    for (let i = -1; i <= 1; i++) {
                        for (let j = -1; j <= 1; j++) {
                            const newRow = row + i;
                            const newCol = col + j;
                            
                            if (newRow >= 0 && newRow < config.rows && 
                                newCol >= 0 && newCol < config.cols &&
                                this.board[newRow][newCol].isMine) {
                                count++;
                            }
                        }
                    }
                    
                    this.board[row][col].neighborMines = count;
                }
            }
        }
    }
    
    renderBoard() {
        const config = this.difficulties[this.currentDifficulty];
        this.gameBoard.style.gridTemplateColumns = `repeat(${config.cols}, 1fr)`;
        this.gameBoard.innerHTML = '';
        
        for (let row = 0; row < config.rows; row++) {
            for (let col = 0; col < config.cols; col++) {
                const cell = document.createElement('div');
                cell.className = 'cell';
                cell.dataset.row = row;
                cell.dataset.col = col;
                
                cell.addEventListener('click', (e) => this.handleCellClick(e));
                cell.addEventListener('contextmenu', (e) => this.handleRightClick(e));
                
                this.gameBoard.appendChild(cell);
            }
        }
        
        this.updateCellDisplay();
    }
    
    updateCellDisplay() {
        const config = this.difficulties[this.currentDifficulty];
        const cells = this.gameBoard.querySelectorAll('.cell');
        
        for (let row = 0; row < config.rows; row++) {
            for (let col = 0; col < config.cols; col++) {
                const cellIndex = row * config.cols + col;
                const cell = cells[cellIndex];
                const cellData = this.board[row][col];
                
                // Reset classes
                cell.className = 'cell';
                cell.textContent = '';
                
                if (cellData.isFlagged) {
                    cell.classList.add('flagged');
                    cell.textContent = '🚩';
                } else if (cellData.isRevealed) {
                    cell.classList.add('revealed');
                    
                    if (cellData.isMine) {
                        cell.classList.add('mine');
                        cell.textContent = '💣';
                    } else if (cellData.neighborMines > 0) {
                        cell.classList.add(`number-${cellData.neighborMines}`);
                        cell.textContent = cellData.neighborMines;
                    }
                }
            }
        }
    }
    
    handleCellClick(e) {
        if (this.gameState === 'won' || this.gameState === 'lost') return;
        
        const row = parseInt(e.target.dataset.row);
        const col = parseInt(e.target.dataset.col);
        const cellData = this.board[row][col];
        
        if (cellData.isFlagged || cellData.isRevealed) return;
        
        // First click - place mines and start timer
        if (this.firstClick) {
            this.placeMines(row, col);
            this.startTimer();
            this.firstClick = false;
            this.gameState = 'playing';
        }
        
        this.revealCell(row, col);
        this.updateCellDisplay();
        this.checkGameState();
    }
    
    handleRightClick(e) {
        e.preventDefault();
        
        if (this.gameState === 'won' || this.gameState === 'lost') return;
        
        const row = parseInt(e.target.dataset.row);
        const col = parseInt(e.target.dataset.col);
        const cellData = this.board[row][col];
        
        if (cellData.isRevealed) return;
        
        cellData.isFlagged = !cellData.isFlagged;
        this.flagCount += cellData.isFlagged ? 1 : -1;
        
        this.updateCellDisplay();
        this.updateDisplay();
    }
    
    revealCell(row, col) {
        const config = this.difficulties[this.currentDifficulty];
        const cellData = this.board[row][col];
        
        if (cellData.isRevealed || cellData.isFlagged) return;
        
        cellData.isRevealed = true;
        
        if (cellData.isMine) {
            this.endGame(false);
            return;
        }
        
        // Flood fill for empty cells
        if (cellData.neighborMines === 0) {
            for (let i = -1; i <= 1; i++) {
                for (let j = -1; j <= 1; j++) {
                    const newRow = row + i;
                    const newCol = col + j;
                    
                    if (newRow >= 0 && newRow < config.rows && 
                        newCol >= 0 && newCol < config.cols) {
                        this.revealCell(newRow, newCol);
                    }
                }
            }
        }
    }
    
    checkGameState() {
        const config = this.difficulties[this.currentDifficulty];
        let revealedCount = 0;
        let totalSafeCells = config.rows * config.cols - config.mines;
        
        for (let row = 0; row < config.rows; row++) {
            for (let col = 0; col < config.cols; col++) {
                if (this.board[row][col].isRevealed && !this.board[row][col].isMine) {
                    revealedCount++;
                }
            }
        }
        
        if (revealedCount === totalSafeCells) {
            this.endGame(true);
        }
    }
    
    endGame(won) {
        this.gameState = won ? 'won' : 'lost';
        this.stopTimer();
        
        const config = this.difficulties[this.currentDifficulty];
        
        if (won) {
            this.resetButton.textContent = '😎';
            this.gameMessage.textContent = 'You Won! 🎉';
            this.gameMessage.className = 'game-message win';
            
            // Auto-flag remaining mines
            for (let row = 0; row < config.rows; row++) {
                for (let col = 0; col < config.cols; col++) {
                    if (this.board[row][col].isMine && !this.board[row][col].isFlagged) {
                        this.board[row][col].isFlagged = true;
                        this.flagCount++;
                    }
                }
            }
        } else {
            this.resetButton.textContent = '😵';
            this.gameMessage.textContent = 'Game Over! 💥';
            this.gameMessage.className = 'game-message lose';
            
            // Reveal all mines
            for (let row = 0; row < config.rows; row++) {
                for (let col = 0; col < config.cols; col++) {
                    if (this.board[row][col].isMine) {
                        this.board[row][col].isRevealed = true;
                    }
                }
            }
        }
        
        this.gameMessage.classList.remove('hidden');
        this.updateCellDisplay();
        this.updateDisplay();
    }
    
    startTimer() {
        this.timerInterval = setInterval(() => {
            this.timer++;
            this.updateDisplay();
        }, 1000);
    }
    
    stopTimer() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
    }
    
    updateDisplay() {
        const config = this.difficulties[this.currentDifficulty];
        const remainingMines = config.mines - this.flagCount;
        
        this.mineCountElement.textContent = remainingMines.toString().padStart(3, '0');
        this.timerElement.textContent = this.timer.toString().padStart(3, '0');
    }
    
    changeDifficulty(difficulty) {
        if (this.difficulties[difficulty]) {
            this.currentDifficulty = difficulty;
            
            // Update active button
            this.difficultyButtons.forEach(btn => {
                btn.classList.toggle('active', btn.dataset.difficulty === difficulty);
            });
            
            this.resetGame();
        }
    }
    
    resetGame() {
        this.gameState = 'ready';
        this.timer = 0;
        this.firstClick = true;
        this.flagCount = 0;
        
        this.stopTimer();
        this.resetButton.textContent = '🙂';
        this.gameMessage.classList.add('hidden');
        
        this.createBoard();
        this.renderBoard();
        this.updateDisplay();
    }
}

// Initialize the game when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new Minesweeper();
});
