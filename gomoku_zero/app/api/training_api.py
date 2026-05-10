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
import logging
import time
from pathlib import Path

logger = logging.getLogger(__name__)
router = APIRouter()

model_manager = ModelManager()

STATE_FILE = Path("training_state.json")

def load_training_state():
    """从文件加载训练状态"""
    try:
        if STATE_FILE.exists():
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load training state: {e}")
    return None

def save_training_state(state: dict):
    """保存训练状态到文件"""
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save training state: {e}")

def init_training_state():
    """初始化训练状态"""
    saved_state = load_training_state()
    if saved_state and saved_state.get('running'):
        logger.info("Found running training from previous session")
        return {
            'running': saved_state.get('running', False),
            'board_size': saved_state.get('board_size', 9),
            'device': saved_state.get('device', 'cpu'),
            'iteration': saved_state.get('iteration', 0),
            'games_completed': saved_state.get('games_completed', 0),
            'loss': saved_state.get('loss', 0.0),
            'thread': None,
            'trainer': None,
            'buffer': None,
            'network': None
        }
    return {
        'running': False,
        'board_size': 9,
        'device': 'cpu',
        'iteration': 0,
        'games_completed': 0,
        'loss': 0.0,
        'thread': None,
        'trainer': None,
        'buffer': None,
        'network': None
    }

training_state = init_training_state()

class StartTrainingRequest(BaseModel):
    board_size: int = 9
    games_per_iteration: int = 100
    mcts_simulations: int = 200
    epochs: int = 10
    device: str = 'cpu'

class TrainingStatusResponse(BaseModel):
    running: bool
    board_size: int
    device: str
    iteration: int
    games_completed: int
    loss: float

class StopResponse(BaseModel):
    message: str

class DeviceInfoResponse(BaseModel):
    cuda_available: bool
    current_device: str
    device_count: int
    device_name: str = ""

@router.get("/devices", response_model=DeviceInfoResponse)
async def get_devices():
    cuda_available = torch.cuda.is_available()
    device_count = torch.cuda.device_count() if cuda_available else 0
    device_name = ""

    if cuda_available:
        device_name = torch.cuda.get_device_name(0)

    return DeviceInfoResponse(
        cuda_available=cuda_available,
        current_device='cuda' if cuda_available else 'cpu',
        device_count=device_count,
        device_name=device_name
    )

@router.post("/start")
async def start_training(request: StartTrainingRequest):
    global training_state

    logger.info(f"Received training request: board_size={request.board_size}, device={request.device}")

    if training_state['running']:
        raise HTTPException(status_code=400, detail="训练已在进行中")

    if request.board_size not in CONFIG.BOARD_SIZES:
        raise HTTPException(status_code=400, detail="不支持的棋盘尺寸")

    if request.device not in ['cpu', 'cuda']:
        raise HTTPException(status_code=400, detail="不支持的设备类型")

    if request.device == 'cuda' and not torch.cuda.is_available():
        raise HTTPException(status_code=400, detail="CUDA不可用，请使用CPU训练")

    training_state['running'] = True
    training_state['board_size'] = request.board_size
    training_state['device'] = request.device
    training_state['iteration'] = 0
    training_state['games_completed'] = 0
    training_state['loss'] = 0.0

    save_training_state({
        'running': True,
        'board_size': request.board_size,
        'device': request.device,
        'iteration': 0,
        'games_completed': 0,
        'loss': 0.0
    })

    def training_loop():
        global training_state
        logger.info(f"Training loop starting with device: {request.device}")
        device = torch.device(request.device)
        network = model_manager.load_model(request.board_size)
        if network is None:
            network = model_manager.create_new_model(request.board_size)

        network = network.to(device)
        logger.info(f"Network moved to device: {next(network.parameters()).device}")

        trainer = Trainer(network, request.board_size)
        buffer = DataBuffer(board_size=request.board_size)

        training_state['trainer'] = trainer
        training_state['buffer'] = buffer
        training_state['network'] = network

        iteration = 0
        games_completed = 0

        while training_state['running']:
            iteration += 1
            training_state['iteration'] = iteration

            logger.info(f"Starting iteration {iteration}, generating {request.games_per_iteration} games...")

            sp = SelfPlay(network, board_size=request.board_size,
                        simulations=request.mcts_simulations, device=device)

            games_batch = sp.play_games(request.games_per_iteration)
            for game in games_batch:
                buffer.add_game(game)
                games_completed += 1
                training_state['games_completed'] = games_completed

            logger.info(f"Iteration {iteration}: {games_completed} games completed, buffer size: {buffer.size()}")

            if buffer.size() >= request.epochs * 32:
                logger.info(f"Training with {buffer.size()} samples...")
                states, policies, values = buffer.sample(batch_size=32)
                states_tensor = torch.from_numpy(states).float().to(device)
                policies_tensor = torch.from_numpy(policies).float().to(device)
                values_tensor = torch.from_numpy(values).float().to(device)

                loss = trainer.train_step(states_tensor, policies_tensor, values_tensor)
                training_state['loss'] = loss
                logger.info(f"Iteration {iteration}: loss = {loss:.4f}")

            if iteration % 10 == 0:
                model_manager.save_model(network, request.board_size, "best")

            save_training_state({
                'running': True,
                'board_size': request.board_size,
                'device': request.device,
                'iteration': iteration,
                'games_completed': games_completed,
                'loss': training_state['loss']
            })

        training_state['running'] = False
        save_training_state({
            'running': False,
            'board_size': request.board_size,
            'device': request.device,
            'iteration': iteration,
            'games_completed': games_completed,
            'loss': training_state['loss']
        })
        logger.info("Training loop finished")

    training_state['thread'] = threading.Thread(target=training_loop)
    training_state['thread'].start()

    return {
        "success": True,
        "message": "训练已开始",
        "board_size": request.board_size,
        "device": request.device
    }

@router.get("/status", response_model=TrainingStatusResponse)
async def get_training_status():
    saved_state = load_training_state()
    if saved_state and saved_state.get('running') and not training_state['running']:
        return TrainingStatusResponse(
            running=True,
            board_size=saved_state.get('board_size', 9),
            device=saved_state.get('device', 'cpu'),
            iteration=saved_state.get('iteration', 0),
            games_completed=saved_state.get('games_completed', 0),
            loss=saved_state.get('loss', 0.0)
        )

    return TrainingStatusResponse(
        running=training_state['running'],
        board_size=training_state['board_size'],
        device=training_state['device'],
        iteration=training_state['iteration'],
        games_completed=training_state['games_completed'],
        loss=training_state['loss']
    )

@router.post("/stop")
async def stop_training():
    global training_state
    training_state['running'] = False

    save_training_state({
        'running': False,
        'board_size': training_state['board_size'],
        'device': training_state['device'],
        'iteration': training_state['iteration'],
        'games_completed': training_state['games_completed'],
        'loss': training_state['loss']
    })

    if training_state['thread']:
        training_state['thread'].join(timeout=5)

    return {"message": "训练已停止"}

@router.get("/history")
async def get_training_history():
    return {
        "iterations": training_state['iteration'],
        "games": training_state['games_completed']
    }
