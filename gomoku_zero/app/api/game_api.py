from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.game.board import Board
from app.game.mcts import MCTS
from app.models.model_manager import ModelManager
from app.config import CONFIG
import uuid
import json
from pathlib import Path

router = APIRouter()

model_manager = ModelManager()
active_games = {}
game_history = []
history_dir = Path("game_history")
history_dir.mkdir(exist_ok=True)

class StartGameRequest(BaseModel):
    board_size: int = 9
    player_color: str = "black"
    model_size: Optional[int] = None

class StartGameResponse(BaseModel):
    game_id: str
    board_size: int
    player_color: str
    ai_color: str

class MoveRequest(BaseModel):
    game_id: str
    position: List[int]

class MoveResponse(BaseModel):
    valid: bool
    game_over: bool
    winner: Optional[int] = None
    ai_position: Optional[List[int]] = None

class GameStateResponse(BaseModel):
    game_id: str
    board: List[List[int]]
    current_player: str
    last_move: Optional[List[int]]
    ai_probabilities: Optional[List[float]]

class GameRecord(BaseModel):
    game_id: str
    board_size: int
    player_color: str
    ai_color: str
    winner: int
    moves: List[dict]
    timestamp: str

class GameHistoryResponse(BaseModel):
    games: List[GameRecord]
    total: int

@router.post("/start", response_model=StartGameResponse)
async def start_game(request: StartGameRequest):
    if request.board_size not in CONFIG.BOARD_SIZES:
        raise HTTPException(status_code=400, detail="不支持的棋盘尺寸")
    
    model_size = request.model_size if request.model_size else request.board_size
    
    network = model_manager.load_model(model_size)
    if network is None:
        network = model_manager.create_new_model(request.board_size)
    
    game_id = str(uuid.uuid4())
    board = Board(size=request.board_size)
    
    if request.player_color == "black":
        player_color = Board.BLACK
        ai_color = Board.WHITE
    else:
        player_color = Board.WHITE
        ai_color = Board.BLACK
    
    active_games[game_id] = {
        'board': board,
        'network': network,
        'player_color': player_color,
        'ai_color': ai_color,
        'mcts': None,
        'moves': [],
        'start_time': datetime.now().isoformat()
    }
    
    return StartGameResponse(
        game_id=game_id,
        board_size=request.board_size,
        player_color=request.player_color,
        ai_color="white" if ai_color == Board.WHITE else "black"
    )

@router.post("/move", response_model=MoveResponse)
async def make_move(request: MoveRequest):
    if request.game_id not in active_games:
        raise HTTPException(status_code=404, detail="游戏不存在")
    
    game = active_games[request.game_id]
    board = game['board']
    
    if board.is_game_over():
        return MoveResponse(
            valid=False,
            game_over=True,
            winner=board.get_winner()
        )
    
    if board.current_player != game['player_color']:
        return MoveResponse(valid=False, game_over=False, winner=None)
    
    row, col = request.position
    if not board.place_stone(row, col):
        return MoveResponse(valid=False, game_over=False, winner=None)
    
    player_move = {'player': 'human', 'position': [row, col], 'turn': len(game['moves']) + 1}
    game['moves'].append(player_move)
    
    if board.is_game_over():
        winner = board.get_winner()
        if game['mcts']:
            game['mcts'].cleanup()
            game['mcts'] = None
        await save_game_to_history(request.game_id, winner)
        return MoveResponse(
            valid=True,
            game_over=True,
            winner=winner
        )
    
    if game['mcts']:
        game['mcts'].cleanup()
    
    mcts = MCTS(board, game['network'], simulations=CONFIG.MCTS_SIMULATIONS)
    mcts.search()
    ai_move = mcts.get_best_move()
    mcts.cleanup()
    
    if ai_move:
        board.place_stone(*ai_move)
        ai_move_record = {'player': 'ai', 'position': list(ai_move), 'turn': len(game['moves']) + 1}
        game['moves'].append(ai_move_record)
    
    if board.is_game_over():
        winner = board.get_winner()
        await save_game_to_history(request.game_id, winner)
        return MoveResponse(
            valid=True,
            game_over=board.is_game_over(),
            winner=winner,
            ai_position=list(ai_move) if ai_move else None
        )
    
    return MoveResponse(
        valid=True,
        game_over=False,
        ai_position=list(ai_move) if ai_move else None
    )

async def save_game_to_history(game_id: str, winner: int):
    if game_id in active_games:
        game = active_games[game_id]
        game_record = {
            'game_id': game_id,
            'board_size': game['board'].size,
            'player_color': 'black' if game['player_color'] == Board.BLACK else 'white',
            'ai_color': 'white' if game['ai_color'] == Board.WHITE else 'black',
            'winner': winner,
            'winner_name': '玩家' if ((winner == 1 and game['player_color'] == Board.BLACK) or (winner == -1 and game['player_color'] == Board.WHITE)) else 'AI' if winner != 0 else '平局',
            'moves': game['moves'],
            'timestamp': game['start_time']
        }
        
        game_history.insert(0, game_record)
        
        if len(game_history) > 50:
            game_history.pop()
        
        history_file = history_dir / f"{game_id}.json"
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(game_record, f, ensure_ascii=False, indent=2)

@router.get("/state/{game_id}", response_model=GameStateResponse)
async def get_game_state(game_id: str):
    if game_id not in active_games:
        raise HTTPException(status_code=404, detail="游戏不存在")
    
    game = active_games[game_id]
    board = game['board']
    
    ai_probs = None
    last_move = None
    if game['mcts'] is not None:
        ai_probs = game['mcts'].get_policy_numpy().tolist()
        if game['mcts'].root:
            last_move = game['mcts'].root.move if game['mcts'].root.move else None
    
    return GameStateResponse(
        game_id=game_id,
        board=board.board.tolist(),
        current_player="black" if board.current_player == Board.BLACK else "white",
        last_move=list(last_move) if last_move else None,
        ai_probabilities=ai_probs
    )

@router.delete("/{game_id}")
async def end_game(game_id: str):
    if game_id in active_games:
        game = active_games[game_id]
        if not game['board'].is_game_over():
            winner = 0
            game_record = {
                'game_id': game_id,
                'board_size': game['board'].size,
                'player_color': 'black' if game['player_color'] == Board.BLACK else 'white',
                'ai_color': 'white' if game['ai_color'] == Board.WHITE else 'black',
                'winner': 0,
                'winner_name': '中断',
                'moves': game['moves'],
                'timestamp': game['start_time']
            }
            game_history.insert(0, game_record)
            
            history_file = history_dir / f"{game_id}.json"
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(game_record, f, ensure_ascii=False, indent=2)
        
        del active_games[game_id]
    
    return {"message": "游戏已结束"}

@router.get("/history", response_model=GameHistoryResponse)
async def get_game_history():
    return GameHistoryResponse(
        games=game_history[:20],
        total=len(game_history)
    )

@router.get("/history/{game_id}")
async def get_game_detail(game_id: str):
    history_file = history_dir / f"{game_id}.json"
    
    if history_file.exists():
        with open(history_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    for game in game_history:
        if game['game_id'] == game_id:
            return game
    
    raise HTTPException(status_code=404, detail="对局记录不存在")
