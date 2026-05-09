/**
 * GomokuZero 主应用逻辑
 */

let boardRenderer;
let replayRenderer;
let game;
let pollInterval;
let currentReplay = null;
let replayStep = 0;

document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

function initApp() {
    const canvas = document.getElementById('game-board');
    boardRenderer = new BoardRenderer(canvas, 15);
    
    const container = document.querySelector('.board-container');
    boardRenderer.resize(container.clientWidth - 40);
    
    window.addEventListener('resize', () => {
        const activeSection = document.querySelector('.tab-content.active');
        if (activeSection && activeSection.id === 'game-section') {
            boardRenderer.resize(container.clientWidth - 40);
        }
    });
    
    canvas.addEventListener('click', handleBoardClick);
    
    initTabs();
    initGameControls();
    initTrainingControls();
    initDataView();
}

function initTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.dataset.tab;
            
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
            btn.classList.add('active');
            document.getElementById(`${tabId}-section`).classList.add('active');
            
            if (tabId === 'game') {
                const container = document.querySelector('.board-container');
                boardRenderer.resize(container.clientWidth - 40);
            } else if (tabId === 'data') {
                loadGameHistory();
            }
        });
    });
}

function initGameControls() {
    const startBtn = document.getElementById('start-game-btn');
    const newGameBtn = document.getElementById('new-game-btn');
    
    startBtn.addEventListener('click', startNewGame);
    newGameBtn.addEventListener('click', startNewGame);
}

async function startNewGame() {
    const boardSize = parseInt(document.getElementById('board-size').value);
    const playerColor = document.getElementById('player-color').value;
    
    game = new GomokuGame();
    boardRenderer.setSize(boardSize);
    
    const container = document.querySelector('.board-container');
    boardRenderer.resize(container.clientWidth - 40);
    
    const result = await game.startGame(boardSize, playerColor);
    
    if (result.success) {
        document.getElementById('status-message').textContent = '游戏开始！';
        document.getElementById('game-actions').classList.remove('hidden');
        boardRenderer.clearPolicyMap();
        
        updateGameState();
    } else {
        showNotification('启动游戏失败: ' + result.error);
    }
}

async function handleBoardClick(event) {
    if (!game || game.gameOver) return;
    
    const cell = boardRenderer.getCellFromEvent(event);
    if (!cell) return;
    
    const [row, col] = cell;
    
    if (game.board && game.board[row] && game.board[row][col] !== 0) {
        showNotification('该位置已有棋子');
        return;
    }
    
    const result = await game.makeMove(row, col);
    
    if (result.success) {
        updateGameState();
        
        if (result.data.game_over) {
            game.gameOver = true;
            game.isMyTurn = false;
            handleGameOver(result.data.winner);
        }
    }
}

async function updateGameState() {
    if (!game || !game.gameId) return;
    
    const state = await game.getGameState();
    if (!state) return;
    
    boardRenderer.setBoard(state.board);
    game.board = state.board;
    
    if (state.last_move) {
        boardRenderer.setLastMove(state.last_move);
    }
    
    if (state.ai_probabilities) {
        boardRenderer.setPolicyMap(state.ai_probabilities);
    }
    
    const statusMsg = document.getElementById('status-message');
    if (state.current_player === game.playerColor) {
        statusMsg.textContent = '轮到你了';
        game.isMyTurn = true;
    } else {
        statusMsg.textContent = 'AI思考中...';
        game.isMyTurn = false;
        setTimeout(updateGameState, 500);
    }
}

function handleGameOver(winner) {
    boardRenderer.clearPolicyMap();
    
    let message;
    if (winner === 0) {
        message = '平局！';
    } else if ((winner === 1 && game.playerColor === 'black') || 
               (winner === -1 && game.playerColor === 'white')) {
        message = '🎉 恭喜获胜！';
    } else {
        message = 'AI获胜，再接再厉！';
    }
    
    document.getElementById('status-message').textContent = message;
    showNotification(message);
    
    loadGameHistory();
}

function initTrainingControls() {
    const startBtn = document.getElementById('start-training-btn');
    const stopBtn = document.getElementById('stop-training-btn');
    const refreshBtn = document.getElementById('refresh-history-btn');
    
    startBtn.addEventListener('click', startTraining);
    stopBtn.addEventListener('click', stopTraining);
    refreshBtn.addEventListener('click', loadGameHistory);
    
    initReplayControls();
    loadDeviceInfo();
    setInterval(updateTrainingStatus, 2000);
}

async function loadDeviceInfo() {
    try {
        const response = await fetch('/api/training/devices');
        const data = await response.json();
        
        const deviceStatus = document.getElementById('device-status');
        if (data.cuda_available) {
            deviceStatus.textContent = `✓ GPU可用: ${data.device_name} | ${data.device_count}个GPU`;
            document.getElementById('train-device').value = 'cuda';
        } else {
            deviceStatus.textContent = '⚠ 仅CPU可用，GPU训练需要CUDA支持';
            document.getElementById('train-device').value = 'cpu';
        }
    } catch (error) {
        console.error('Load device info error:', error);
    }
}

async function startTraining() {
    const device = document.getElementById('train-device').value;
    const boardSize = parseInt(document.getElementById('train-board-size').value);
    const gamesPerIter = parseInt(document.getElementById('games-per-iter').value);
    const mctsSim = parseInt(document.getElementById('mcts-sim').value);
    const trainEpochs = parseInt(document.getElementById('train-epochs').value);
    
    try {
        const response = await fetch('/api/training/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                board_size: boardSize,
                games_per_iteration: gamesPerIter,
                mcts_simulations: mctsSim,
                train_epochs: trainEpochs,
                device: device
            })
        });
        
        const data = await response.json();
        
        document.getElementById('start-training-btn').classList.add('hidden');
        document.getElementById('stop-training-btn').classList.remove('hidden');
        document.getElementById('training-status').classList.remove('hidden');
        document.getElementById('stat-device').textContent = device.toUpperCase();
        
        showNotification(`训练已开始 (${device.toUpperCase()})`);
    } catch (error) {
        showNotification('启动训练失败: ' + error.message);
    }
}

async function stopTraining() {
    try {
        await fetch('/api/training/stop', { method: 'POST' });
        
        document.getElementById('start-training-btn').classList.remove('hidden');
        document.getElementById('stop-training-btn').classList.add('hidden');
        
        showNotification('训练已停止');
    } catch (error) {
        showNotification('停止训练失败: ' + error.message);
    }
}

async function updateTrainingStatus() {
    try {
        const response = await fetch('/api/training/status');
        const data = await response.json();
        
        if (data.running) {
            document.getElementById('stat-iteration').textContent = data.iteration;
            document.getElementById('stat-games').textContent = data.games_completed;
            document.getElementById('stat-loss').textContent = data.loss.toFixed(4);
            document.getElementById('stat-device').textContent = data.device.toUpperCase();
        }
    } catch (error) {
        console.error('Update training status error:', error);
    }
}

async function initDataView() {
    await loadModelList();
    await loadTrainingStats();
    await loadGameHistory();
}

async function loadModelList() {
    try {
        const response = await fetch('/api/data/models');
        const data = await response.json();
        
        const modelList = document.getElementById('model-list');
        
        if (!data.models || data.models.length === 0) {
            modelList.innerHTML = '<p class="empty">暂无训练模型</p>';
            return;
        }
        
        modelList.innerHTML = data.models.map(model => `
            <div class="model-card">
                <h4>${model.board_size}×${model.board_size} 棋盘</h4>
                <p>通道数: ${model.num_channels}</p>
                <p>残差块: ${model.num_res_blocks}</p>
            </div>
        `).join('');
    } catch (error) {
        console.error('Load model list error:', error);
    }
}

async function loadGameHistory() {
    try {
        const response = await fetch('/api/game/history');
        const data = await response.json();
        
        const historyList = document.getElementById('game-history-list');
        
        if (!data.games || data.games.length === 0) {
            historyList.innerHTML = '<p class="empty">暂无对局记录</p>';
            return;
        }
        
        historyList.innerHTML = data.games.map(game => {
            const isWin = game.winner_name === '玩家';
            const isDraw = game.winner_name === '平局';
            const badgeClass = isWin ? 'win' : (isDraw ? 'draw' : 'lose');
            
            return `
                <div class="history-card ${badgeClass}" onclick="openReplay('${game.game_id}')">
                    <h4>${game.board_size}×${game.board_size} 对局</h4>
                    <div class="info">你执: ${game.player_color === 'black' ? '黑棋' : '白棋'}</div>
                    <div class="info">回合数: ${game.moves.length}</div>
                    <div class="info">时间: ${new Date(game.timestamp).toLocaleString('zh-CN')}</div>
                    <span class="winner-badge ${badgeClass}">${game.winner_name}${isWin ? '获胜' : (isDraw ? '' : '失败')}</span>
                </div>
            `;
        }).join('');
    } catch (error) {
        console.error('Load game history error:', error);
        document.getElementById('game-history-list').innerHTML = '<p class="empty">加载失败</p>';
    }
}

async function loadTrainingStats() {
    try {
        const response = await fetch('/api/training/history');
        const data = await response.json();
        
        document.getElementById('total-games').textContent = data.games;
        document.getElementById('total-iterations').textContent = data.iterations;
    } catch (error) {
        console.error('Load training stats error:', error);
    }
}

function initReplayControls() {
    document.getElementById('replay-start').addEventListener('click', () => {
        replayStep = 0;
        updateReplay();
    });
    
    document.getElementById('replay-prev').addEventListener('click', () => {
        if (replayStep > 0) {
            replayStep--;
            updateReplay();
        }
    });
    
    document.getElementById('replay-next').addEventListener('click', () => {
        if (currentReplay && replayStep < currentReplay.moves.length) {
            replayStep++;
            updateReplay();
        }
    });
    
    document.getElementById('replay-end').addEventListener('click', () => {
        if (currentReplay) {
            replayStep = currentReplay.moves.length;
            updateReplay();
        }
    });
    
    document.getElementById('close-replay-btn').addEventListener('click', closeReplay);
}

async function openReplay(gameId) {
    try {
        const response = await fetch(`/api/game/history/${gameId}`);
        currentReplay = await response.json();
        
        if (!replayRenderer) {
            const canvas = document.getElementById('replay-board');
            replayRenderer = new BoardRenderer(canvas, currentReplay.board_size);
        } else {
            replayRenderer.setSize(currentReplay.board_size);
        }
        
        replayStep = 0;
        
        const replaySection = document.getElementById('replay-section');
        replaySection.classList.remove('hidden');
        
        updateReplay();
        
        document.getElementById('replay-section').scrollIntoView({ behavior: 'smooth' });
    } catch (error) {
        console.error('Open replay error:', error);
        showNotification('加载回放失败');
    }
}

function updateReplay() {
    if (!currentReplay) return;
    
    const board = Array(currentReplay.board_size).fill().map(() => Array(currentReplay.board_size).fill(0));
    let lastMove = null;
    
    for (let i = 0; i < replayStep && i < currentReplay.moves.length; i++) {
        const move = currentReplay.moves[i];
        const player = move.player === 'human' ? (currentReplay.player_color === 'black' ? 1 : -1) : (currentReplay.ai_color === 'black' ? 1 : -1);
        board[move.position[0]][move.position[1]] = player;
        lastMove = move.position;
    }
    
    replayRenderer.setBoard(board);
    replayRenderer.setLastMove(lastMove);
    
    const container = document.querySelector('#replay-section .board-container');
    replayRenderer.resize(Math.min(container.clientWidth - 40, 500));
    
    document.getElementById('replay-step').textContent = `${replayStep} / ${currentReplay.moves.length}`;
}

function closeReplay() {
    currentReplay = null;
    replayStep = 0;
    document.getElementById('replay-section').classList.add('hidden');
}

function showNotification(message) {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.classList.remove('hidden');
    
    setTimeout(() => {
        notification.classList.add('hidden');
    }, 3000);
}
