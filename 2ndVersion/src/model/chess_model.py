import torch
import torch.nn as nn
import torch.nn.functional as F


class ChessNet(nn.Module):
    def __init__(self, device='cpu'):
        super(ChessNet, self).__init__()
        self.device = device
        
        self.conv1 = nn.Conv2d(12, 128, 3, padding=1)
        self.conv2 = nn.Conv2d(128, 128, 3, padding=1)
        self.conv3 = nn.Conv2d(128, 128, 3, padding=1)
        
        self.bn1 = nn.BatchNorm2d(128)
        self.bn2 = nn.BatchNorm2d(128)
        self.bn3 = nn.BatchNorm2d(128)
        
        self.policy_conv = nn.Conv2d(128, 73, 1)
        self.policy_bn = nn.BatchNorm2d(73)
        self.policy_fc = nn.Linear(73 * 64, 4672)
        
        self.value_conv = nn.Conv2d(128, 32, 1)
        self.value_bn = nn.BatchNorm2d(32)
        self.value_fc1 = nn.Linear(32 * 64, 128)
        self.value_fc2 = nn.Linear(128, 1)
        
    def forward(self, x):
        # Shared layers
        x = F.relu(self.bn1(self.conv1(x)))
        x = F.relu(self.bn2(self.conv2(x)))
        x = F.relu(self.bn3(self.conv3(x)))
        
        policy = F.relu(self.policy_bn(self.policy_conv(x)))
        policy = policy.view(-1, 73 * 64)
        policy = self.policy_fc(policy)
        policy = F.log_softmax(policy, dim=1)

        value = F.relu(self.value_bn(self.value_conv(x)))
        value = value.view(-1, 32 * 64)
        value = F.relu(self.value_fc1(value))
        value = torch.tanh(self.value_fc2(value))
        
        return policy, value
