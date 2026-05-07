from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.models.model_manager import ModelManager
from app.training.trainer import Trainer
from app.training.data_buffer import DataBuffer
from app.game.self_play import SelfPlay
from app.config import CONFIG
import torch
import threading
import json
from datetime import datetime

router = APIRouter()

model_manager = ModelManager()

training_state = {
    'running': False,
    'board_size': 9,
    'iteration': 0,
    'games_completed': 0,
    'loss': 0.0,
    'thread': None,
    'trainer': None,
    'buffer': None,
    'network': None
}

class StartTrainingRequest(BaseModel):
    board_size: int = 9
    games_per_iteration: int = 100
    mcts_simulations: int = 200
    train_epochs: int = 10

class TrainingStatusResponse(BaseModel):
    running: bool
    board_size: int
    iteration: int
    games_completed: int
    loss: float

class StopResponse(BaseModel):
    message: str

@router.post("/start")
async def start_training(request: StartTrainingRequest):
    global training_state
    
    if training_state['running']:
        raise HTTPException(status_code=400, detail="训练已在进行中")
    
    if request.board_size not in CONFIG.BOARD_SIZES:
        raise HTTPException(status_code=400, detail="不支持的棋盘尺寸")
    
    training_state['running'] = True
    training_state['board_size'] = request.board_size
    training_state['iteration'] = 0
    training_state['games_completed'] = 0
    
    def training_loop():
        network = model_manager.load_model(request.board_size)
        if network is None:
            network = model_manager.create_new_model(request.board_size)
        
        trainer = Trainer(network, request.board_size)
        buffer = DataBuffer(board_size=request.board_size)
        
        training_state['trainer'] = trainer
        training_state['buffer'] = buffer
        training_state['network'] = network
        
        iteration = 0
        while training_state['running']:
            iteration += 1
            training_state['iteration'] = iteration
            
            sp = SelfPlay(network, board_size=request.board_size, 
                        simulations=request.mcts_simulations)
            
            games_batch = sp.play_games(request.games_per_iteration)
            for game in games_batch:
                buffer.add_game(game)
                training_state['games_completed'] += 1
            
            if buffer.size() >= request.train_epochs * 32:
                states, policies, values = buffer.sample(batch_size=32)
                states_tensor = torch.from_numpy(states).float()
                policies_tensor = torch.from_numpy(policies).float()
                values_tensor = torch.from_numpy(values).float()
                
                loss = trainer.train_step(states_tensor, policies_tensor, values_tensor)
                training_state['loss'] = loss
            
            if iteration % 10 == 0:
                model_manager.save_model(network, request.board_size, "best")
    
    training_state['thread'] = threading.Thread(target=training_loop)
    training_state['thread'].start()
    
    return {"message": "训练已开始", "board_size": request.board_size}

@router.get("/status", response_model=TrainingStatusResponse)
async def get_training_status():
    return TrainingStatusResponse(
        running=training_state['running'],
        board_size=training_state['board_size'],
        iteration=training_state['iteration'],
        games_completed=training_state['games_completed'],
        loss=training_state['loss']
    )

@router.post("/stop", response_model=StopResponse)
async def stop_training():
    global training_state
    training_state['running'] = False
    if training_state['thread']:
        training_state['thread'].join()
    return StopResponse(message="训练已停止")

@router.get("/history")
async def get_training_history():
    return {
        "iterations": training_state['iteration'], 
        "games": training_state['games_completed']
    }
