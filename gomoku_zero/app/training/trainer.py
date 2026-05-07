import torch
import torch.nn as nn
import torch.optim as optim
from typing import List
import numpy as np

class Trainer:
    def __init__(self, network, board_size: int, 
                 learning_rate: float = 0.01,
                 weight_decay: float = 1e-4,
                 l2_reg: float = 1e-4):
        self.network = network
        self.board_size = board_size
        self.l2_reg = l2_reg
        
        self.optimizer = optim.Adam(
            network.parameters(),
            lr=learning_rate,
            weight_decay=weight_decay
        )
        
        self.scheduler = optim.lr_scheduler.StepLR(
            self.optimizer,
            step_size=10,
            gamma=0.9
        )
    
    def train_step(self, states: torch.Tensor, target_policies: torch.Tensor, 
                   target_values: torch.Tensor) -> float:
        self.network.train()
        
        self.optimizer.zero_grad()
        
        policies, values = self.network(states)
        
        policy_loss = -torch.mean(
            target_policies * torch.log(policies + 1e-8)
        )
        
        value_loss = torch.mean((values - target_values) ** 2)
        
        l2_loss = sum(
            torch.sum(param ** 2) for param in self.network.parameters()
        )
        
        total_loss = policy_loss + value_loss + self.l2_reg * l2_loss
        
        total_loss.backward()
        
        torch.nn.utils.clip_grad_norm_(self.network.parameters(), 1.0)
        
        self.optimizer.step()
        
        return total_loss.item()
    
    def eval_step(self, states: torch.Tensor, target_policies: torch.Tensor,
                  target_values: torch.Tensor) -> dict:
        self.network.eval()
        
        with torch.no_grad():
            policies, values = self.network(states)
            
            policy_loss = -torch.mean(
                target_policies * torch.log(policies + 1e-8)
            )
            
            value_loss = torch.mean((values - target_values) ** 2)
            
            policy_acc = torch.mean(
                (torch.argmax(policies, dim=1) == torch.argmax(target_policies, dim=1)).float()
            )
        
        return {
            'policy_loss': policy_loss.item(),
            'value_loss': value_loss.item(),
            'policy_accuracy': policy_acc.item()
        }
    
    def train_on_batch(self, states: np.ndarray, policies: np.ndarray, 
                      values: np.ndarray, epochs: int = 1) -> List[float]:
        states_tensor = torch.from_numpy(states).float()
        policies_tensor = torch.from_numpy(policies).float()
        values_tensor = torch.from_numpy(values).float()
        
        losses = []
        for _ in range(epochs):
            loss = self.train_step(states_tensor, policies_tensor, values_tensor)
            losses.append(loss)
        
        return losses
    
    def step(self):
        self.scheduler.step()
        return self.scheduler.get_last_lr()[0]
    
    def save_checkpoint(self, path: str, iteration: int):
        torch.save({
            'iteration': iteration,
            'model_state_dict': self.network.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict()
        }, path)
    
    def load_checkpoint(self, path: str):
        checkpoint = torch.load(path)
        self.network.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
        return checkpoint['iteration']
