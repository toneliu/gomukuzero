from dataclasses import dataclass
from typing import List

@dataclass
class Config:
    BOARD_SIZES: List[int] = None
    DEFAULT_BOARD_SIZE: int = 9
    HISTORY_LEN: int = 4
    
    NUM_CHANNELS: int = 128
    NUM_RES_BLOCKS: int = 10
    
    MCTS_SIMULATIONS: int = 200
    C_PUCT: float = 1.5
    DIRICHLET_ALPHA: float = 0.03
    FPU_REDUCTION: float = 0.25
    
    BATCH_SIZE: int = 128
    LEARNING_RATE: float = 0.01
    LR_DECAY: float = 0.9
    WEIGHT_DECAY: float = 1e-4
    
    SELF_PLAY_GAMES: int = 500
    TEMPERATURE: float = 1.0
    
    def __post_init__(self):
        if self.BOARD_SIZES is None:
            self.BOARD_SIZES = [9, 11, 13, 15, 19]

CONFIG = Config()
