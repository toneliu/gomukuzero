from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.models.model_manager import ModelManager
from app.config import CONFIG
import os
from pathlib import Path

router = APIRouter()

model_manager = ModelManager()

class ModelInfo(BaseModel):
    board_size: int
    num_channels: int
    num_res_blocks: int
    path: str

class ModelListResponse(BaseModel):
    models: List[ModelInfo]

@router.get("/models", response_model=ModelListResponse)
async def list_models():
    models = model_manager.list_models()
    return ModelListResponse(
        models=[
            ModelInfo(**model) for model in models.values()
        ]
    )

@router.get("/models/{board_size}/info")
async def get_model_info(board_size: int):
    models = model_manager.list_models()
    if board_size not in models:
        raise HTTPException(status_code=404, detail="模型不存在")
    return models[board_size]

@router.get("/config/sizes")
async def get_board_sizes():
    return {"sizes": CONFIG.BOARD_SIZES, "default": CONFIG.DEFAULT_BOARD_SIZE}

@router.get("/config/training")
async def get_training_config():
    return {
        "mcts_simulations": CONFIG.MCTS_SIMULATIONS,
        "batch_size": CONFIG.BATCH_SIZE,
        "learning_rate": CONFIG.LEARNING_RATE,
        "num_channels": CONFIG.NUM_CHANNELS,
        "num_res_blocks": CONFIG.NUM_RES_BLOCKS
    }
