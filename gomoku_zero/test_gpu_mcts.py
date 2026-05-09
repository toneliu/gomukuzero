import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
from app.game.board import Board
from app.models.gomoku_net import GomokuNet

def test_gpu_mcts():
    print("测试 GPU MCTS...")
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"使用设备: {device}")
    
    board_size = 9
    board = Board(size=board_size)
    print(f"创建 {board_size}x{board_size} 棋盘")
    
    network = GomokuNet(board_size=board_size)
    network = network.to(device)
    network.eval()
    print("创建神经网络并移动到 GPU")
    
    from app.game.mcts import MCTS
    
    mcts = MCTS(board, network, simulations=100)
    print("创建 MCTS 实例")
    
    print("\n开始 MCTS 搜索...")
    root_value = mcts.search()
    print(f"MCTS 搜索完成，根节点值: {root_value:.4f}")
    
    policy = mcts.get_policy_numpy(temperature=1.0)
    print(f"策略分布: 最大概率={policy.max():.4f}, 形状={policy.shape}")
    
    best_move = mcts.get_best_move()
    print(f"最佳走法: {best_move}")
    
    if best_move:
        print("✅ GPU MCTS 测试通过！")
    else:
        print("❌ GPU MCTS 测试失败！")
        return False
    
    return True

if __name__ == "__main__":
    try:
        success = test_gpu_mcts()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
