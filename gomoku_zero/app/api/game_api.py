from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.game.board import Board
from app.game.mcts import MCTS
from app.models.model_manager import ModelManager
from app.config import CONFIG
import uuid

router = APIRouter()

model_manager = ModelManager()
active_games = {}

class StartGameRequest(BaseModel):
    board_size: int = 9
    player_color: str = "black"

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

@router.post("/start", response_model=StartGameResponse)
async def start_game(request: StartGameRequest):
    if request.board_size not in CONFIG.BOARD_SIZES:
        raise HTTPException(status_code=400, detail="不支持的棋盘尺寸")
    
    network = model_manager.load_model(request.board_size)
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
        'mcts': None
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
    
    if board.is_game_over():
        return MoveResponse(
            valid=True,
            game_over=True,
            winner=board.get_winner()
        )
    
    mcts = MCTS(board, game['network'], simulations=CONFIG.MCTS_SIMULATIONS)
    mcts.search()
    ai_move = mcts.get_best_move()
    
    if ai_move:
        board.place_stone(*ai_move)
        game['mcts'] = mcts
    
    return MoveResponse(
        valid=True,
        game_over=board.is_game_over(),
        winner=board.get_winner() if board.is_game_over() else None,
        ai_position=list(ai_move) if ai_move else None
    )

@router.get("/state/{game_id}", response_model=GameStateResponse)
async def get_game_state(game_id: str):
    if game_id not in active_games:
        raise HTTPException(status_code=404, detail="游戏不存在")
    
    game = active_games[game_id]
    board = game['board']
    
    ai_probs = None
    if game['mcts']:
        ai_probs = game['mcts'].get_policy().tolist()
    
    return GameStateResponse(
        game_id=game_id,
        board=board.board.tolist(),
        current_player="black" if board.current_player == Board.BLACK else "white",
        last_move=game['mcts'].root.move if game['mcts'] and game['mcts'].root.move else None,
        ai_probabilities=ai_probs
    )

@router.delete("/{game_id}")
async def end_game(game_id: str):
    if game_id in active_games:
        del active_games[game_id]
    return {"message": "游戏已结束"}
