/**
 * 棋盘渲染器 - 负责在Canvas上绘制五子棋棋盘
 */
class BoardRenderer {
    /**
     * @param {HTMLCanvasElement} canvas - Canvas元素
     * @param {number} size - 棋盘大小（默认15）
     */
    constructor(canvas, size = 15) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.size = size;
        this.cellSize = 30;
        this.board = Array(size).fill().map(() => Array(size).fill(0));
        this.lastMove = null;
        this.policyMap = null;
        this.stoneRadius = 0.4;
    }
    
    /**
     * 设置棋盘大小并重置棋盘状态
     * @param {number} size - 新的棋盘大小
     */
    setSize(size) {
        this.size = size;
        this.board = Array(size).fill().map(() => Array(size).fill(0));
        this.lastMove = null;
        this.policyMap = null;
    }
    
    /**
     * 根据容器宽度调整Canvas尺寸
     * @param {number} containerWidth - 容器宽度
     */
    resize(containerWidth) {
        const maxSize = Math.min(containerWidth, 600);
        this.cellSize = Math.floor(maxSize / this.size);
        const canvasSize = this.cellSize * this.size;
        
        const dpr = window.devicePixelRatio || 1;
        this.canvas.width = canvasSize * dpr;
        this.canvas.height = canvasSize * dpr;
        this.canvas.style.width = `${canvasSize}px`;
        this.canvas.style.height = `${canvasSize}px`;
        this.ctx.scale(dpr, dpr);
        
        this.draw();
    }
    
    /**
     * 设置棋盘状态
     * @param {Array<Array<number>>} board - 棋盘状态数组
     */
    setBoard(board) {
        this.board = board;
        this.draw();
    }
    
    /**
     * 设置最后一次落子位置
     * @param {Array<number>} move - [row, col]
     */
    setLastMove(move) {
        this.lastMove = move;
        this.draw();
    }
    
    /**
     * 设置策略热力图（AI落子概率）
     * @param {Array<number>|null} policy - 扁平化的概率数组
     */
    setPolicyMap(policy) {
        if (!policy) {
            this.policyMap = null;
            this.draw();
            return;
        }
        
        this.policyMap = [];
        for (let i = 0; i < this.size; i++) {
            this.policyMap[i] = [];
            for (let j = 0; j < this.size; j++) {
                const idx = i * this.size + j;
                if (this.board[i][j] === 0 && policy[idx] > 0.01) {
                    this.policyMap[i][j] = policy[idx];
                } else {
                    this.policyMap[i][j] = 0;
                }
            }
        }
        this.draw();
    }
    
    /**
     * 清除策略热力图
     */
    clearPolicyMap() {
        this.policyMap = null;
        this.draw();
    }
    
    /**
     * 绘制整个棋盘
     */
    draw() {
        const ctx = this.ctx;
        const cs = this.cellSize;
        
        ctx.clearRect(0, 0, cs * this.size, cs * this.size);
        
        this.drawBackground();
        this.drawGrid();
        if (this.policyMap) {
            this.drawPolicyMap();
        }
        this.drawStones();
    }
    
    /**
     * 绘制棋盘背景色
     */
    drawBackground() {
        const ctx = this.ctx;
        const cs = this.cellSize;
        ctx.fillStyle = '#DEB887';
        ctx.fillRect(0, 0, cs * this.size, cs * this.size);
    }
    
    /**
     * 绘制棋盘网格线
     */
    drawGrid() {
        const ctx = this.ctx;
        const cs = this.cellSize;
        
        ctx.strokeStyle = '#8B4513';
        ctx.lineWidth = 1;
        
        for (let i = 0; i < this.size; i++) {
            ctx.beginPath();
            ctx.moveTo(cs / 2, cs / 2 + i * cs);
            ctx.lineTo(cs * (this.size - 0.5), cs / 2 + i * cs);
            ctx.stroke();
            
            ctx.beginPath();
            ctx.moveTo(cs / 2 + i * cs, cs / 2);
            ctx.lineTo(cs / 2 + i * cs, cs * (this.size - 0.5));
            ctx.stroke();
        }
        
        if (this.size === 15) {
            const starPoints = [[3, 3], [3, 7], [3, 11], [7, 3], [7, 7], [7, 11], [11, 3], [11, 7], [11, 11]];
            ctx.fillStyle = '#8B4513';
            for (const [row, col] of starPoints) {
                ctx.beginPath();
                ctx.arc(cs / 2 + col * cs, cs / 2 + row * cs, cs * 0.1, 0, Math.PI * 2);
                ctx.fill();
            }
        }
    }
    
    /**
     * 绘制策略热力图
     */
    drawPolicyMap() {
        const ctx = this.ctx;
        const cs = this.cellSize;
        
        const maxProb = Math.max(...this.policyMap.flat().filter(v => v > 0));
        if (maxProb === 0) return;
        
        for (let i = 0; i < this.size; i++) {
            for (let j = 0; j < this.size; j++) {
                if (this.policyMap[i][j] > 0) {
                    const alpha = 0.3 + 0.7 * (this.policyMap[i][j] / maxProb);
                    ctx.fillStyle = `rgba(76, 175, 80, ${alpha})`;
                    ctx.beginPath();
                    ctx.arc(cs / 2 + j * cs, cs / 2 + i * cs, cs * 0.4, 0, Math.PI * 2);
                    ctx.fill();
                }
            }
        }
    }
    
    /**
     * 绘制棋子
     */
    drawStones() {
        const ctx = this.ctx;
        const cs = this.cellSize;
        
        for (let i = 0; i < this.size; i++) {
            for (let j = 0; j < this.size; j++) {
                if (this.board[i][j] !== 0) {
                    this.drawStone(j, i, this.board[i][j]);
                    
                    if (this.lastMove && this.lastMove[0] === i && this.lastMove[1] === j) {
                        ctx.strokeStyle = '#f44336';
                        ctx.lineWidth = 2;
                        ctx.beginPath();
                        ctx.arc(cs / 2 + j * cs, cs / 2 + i * cs, cs * 0.35, 0, Math.PI * 2);
                        ctx.stroke();
                    }
                }
            }
        }
    }
    
    /**
     * 绘制单个棋子
     * @param {number} col - 列索引
     * @param {number} row - 行索引
     * @param {number} color - 棋子颜色（1: 黑, -1: 白）
     */
    drawStone(col, row, color) {
        const ctx = this.ctx;
        const cs = this.cellSize;
        const x = cs / 2 + col * cs;
        const y = cs / 2 + row * cs;
        const radius = cs * this.stoneRadius;
        
        const gradient = ctx.createRadialGradient(
            x - radius * 0.25,
            y - radius * 0.25,
            0,
            x,
            y,
            radius
        );
        
        if (color === 1) {
            gradient.addColorStop(0, '#444');
            gradient.addColorStop(1, '#000');
        } else {
            gradient.addColorStop(0, '#fff');
            gradient.addColorStop(1, '#ccc');
        }
        
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(x, y, radius, 0, Math.PI * 2);
        ctx.fill();
        
        ctx.strokeStyle = color === 1 ? '#333' : '#999';
        ctx.lineWidth = 1;
        ctx.stroke();
    }
    
    /**
     * 从鼠标事件获取点击的格子位置
     * @param {MouseEvent} event - 鼠标事件
     * @returns {Array<number>|null} - [row, col] 或 null
     */
    getCellFromEvent(event) {
        const rect = this.canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        
        const cs = this.cellSize;
        const col = Math.round((x - cs / 2) / cs);
        const row = Math.round((y - cs / 2) / cs);
        
        if (row >= 0 && row < this.size && col >= 0 && col < this.size) {
            return [row, col];
        }
        return null;
    }
}
