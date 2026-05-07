import torch
import torch.nn as nn
import torch.nn.functional as F

class ResidualBlock(nn.Module):
    def __init__(self, num_channels: int):
        super().__init__()
        self.conv1 = nn.Conv2d(num_channels, num_channels, 3, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(num_channels)
        self.conv2 = nn.Conv2d(num_channels, num_channels, 3, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(num_channels)
    
    def forward(self, x):
        residual = x
        x = F.relu(self.bn1(self.conv1(x)))
        x = self.bn2(self.conv2(x))
        x = F.relu(x + residual)
        return x

class GomokuNet(nn.Module):
    def __init__(self, board_size: int = 9, num_channels: int = 128, 
                 num_res_blocks: int = 10, history_len: int = 4):
        super().__init__()
        self.board_size = board_size
        self.num_channels = num_channels
        self.num_res_blocks = num_res_blocks
        self.history_len = history_len
        
        self.input_conv = nn.Sequential(
            nn.Conv2d(history_len * 2 + 1, num_channels, 3, padding=1, bias=False),
            nn.BatchNorm2d(num_channels),
            nn.ReLU()
        )
        
        self.residual_blocks = nn.ModuleList([
            ResidualBlock(num_channels) for _ in range(num_res_blocks)
        ])
        
        self.policy_head = nn.Sequential(
            nn.Conv2d(num_channels, 32, 1, bias=False),
            nn.BatchNorm2d(32),
            nn.ReLU(),
        )
        self.policy_head_fc = nn.Linear(32 * board_size * board_size, board_size * board_size)
        
        self.value_head = nn.Sequential(
            nn.Conv2d(num_channels, 32, 1, bias=False),
            nn.BatchNorm2d(32),
            nn.ReLU(),
        )
        self.value_head_fc = nn.Sequential(
            nn.Linear(32 * board_size * board_size, 256),
            nn.ReLU(),
            nn.Linear(256, 1),
            nn.Tanh()
        )
    
    def forward(self, x):
        if x.dim() == 3:
            x = x.unsqueeze(0)
        
        x = self.input_conv(x)
        
        for block in self.residual_blocks:
            x = block(x)
        
        policy = self.policy_head(x)
        policy = policy.view(policy.size(0), -1)
        policy = self.policy_head_fc(policy)
        policy = F.softmax(policy, dim=1)
        
        value = self.value_head(x)
        value = value.view(value.size(0), -1)
        value = self.value_head_fc(value)
        
        return policy, value
    
    def get_policy(self, state):
        policy, _ = self.forward(state)
        return policy
    
    def get_value(self, state):
        _, value = self.forward(state)
        return value
