import torch
import os
from pathlib import Path
from typing import Optional
from .gomoku_net import GomokuNet
from app.config import CONFIG

class ModelManager:
    def __init__(self, models_dir: str = "models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
    
    def get_model_path(self, board_size: int, model_type: str = "best") -> Path:
        return self.models_dir / f"model_{board_size}x{board_size}_{model_type}.pth"
    
    def save_model(self, model: GomokuNet, board_size: int, model_type: str = "best"):
        path = self.get_model_path(board_size, model_type)
        torch.save({
            'model_state_dict': model.state_dict(),
            'board_size': board_size,
            'num_channels': model.num_channels,
            'num_res_blocks': model.num_res_blocks,
            'history_len': model.history_len
        }, path)
        return path
    
    def load_model(self, board_size: int, model_type: str = "best") -> Optional[GomokuNet]:
        path = self.get_model_path(board_size, model_type)
        if not path.exists():
            return None
        
        checkpoint = torch.load(path)
        model = GomokuNet(
            board_size=checkpoint['board_size'],
            num_channels=checkpoint['num_channels'],
            num_res_blocks=checkpoint['num_res_blocks'],
            history_len=checkpoint['history_len']
        )
        model.load_state_dict(checkpoint['model_state_dict'])
        return model
    
    def create_new_model(self, board_size: int) -> GomokuNet:
        return GomokuNet(
            board_size=board_size,
            num_channels=CONFIG.NUM_CHANNELS,
            num_res_blocks=CONFIG.NUM_RES_BLOCKS,
            history_len=CONFIG.HISTORY_LEN
        )
    
    def list_models(self) -> dict:
        models = {}
        for path in self.models_dir.glob("model_*_best.pth"):
            try:
                checkpoint = torch.load(path)
                size = checkpoint['board_size']
                models[size] = {
                    'path': str(path),
                    'board_size': size,
                    'num_channels': checkpoint['num_channels'],
                    'num_res_blocks': checkpoint['num_res_blocks']
                }
            except:
                pass
        return models
