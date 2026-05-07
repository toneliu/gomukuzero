/**
 * GomokuGame - 对弈游戏逻辑类
 */
class GomokuGame {
    constructor() {
        this.gameId = null;
        this.boardSize = 15;
        this.playerColor = 'black';
        this.isMyTurn = false;
        this.gameOver = false;
        this.network = null;
    }
    
    /**
     * 开始新游戏
     * @param {number} boardSize - 棋盘大小
     * @param {string} playerColor - 玩家执棋颜色
     * @returns {Promise<Object>} - 包含success和data/error
     */
    async startGame(boardSize, playerColor) {
        this.boardSize = boardSize;
        this.playerColor = playerColor;
        this.isMyTurn = (playerColor === 'black');
        this.gameOver = false;
        
        try {
            const response = await fetch('/api/game/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    board_size: boardSize,
                    player_color: playerColor
                })
            });
            
            const data = await response.json();
            this.gameId = data.game_id;
            
            return { success: true, data };
        } catch (error) {
            console.error('Start game error:', error);
            return { success: false, error: error.message };
        }
    }
    
    /**
     * 玩家落子
     * @param {number} row - 行索引
     * @param {number} col - 列索引
     * @returns {Promise<Object>} - 包含success和data/error
     */
    async makeMove(row, col) {
        if (!this.gameId || !this.isMyTurn || this.gameOver) {
            return { success: false, reason: 'Not your turn' };
        }
        
        try {
            const response = await fetch('/api/game/move', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    game_id: this.gameId,
                    position: [row, col]
                })
            });
            
            const data = await response.json();
            return { success: data.valid, data };
        } catch (error) {
            console.error('Make move error:', error);
            return { success: false, error: error.message };
        }
    }
    
    /**
     * 获取当前游戏状态
     * @returns {Promise<Object|null>}
     */
    async getGameState() {
        if (!this.gameId) return null;
        
        try {
            const response = await fetch(`/api/game/state/${this.gameId}`);
            return await response.json();
        } catch (error) {
            console.error('Get state error:', error);
            return null;
        }
    }
    
    /**
     * 结束游戏
     */
    async endGame() {
        if (!this.gameId) return;
        
        try {
            await fetch(`/api/game/${this.gameId}`, { method: 'DELETE' });
        } catch (error) {
            console.error('End game error:', error);
        }
        
        this.gameId = null;
    }
}
