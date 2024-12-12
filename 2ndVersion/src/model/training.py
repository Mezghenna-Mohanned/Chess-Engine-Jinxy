import torch
import torch.optim as optim
import numpy as np

class ChessTrainer:
    def __init__(self, model, device='cpu', learning_rate=0.001):
        self.device = device
        self.model = model.to(device)
        self.optimizer = optim.Adam(model.parameters(), lr=learning_rate)
        
    def train_step(self, states, target_policies, target_values, batch_size=32):
        states = np.array(states)
        target_policies = np.array(target_policies)
        target_values = np.array(target_values)

        states = torch.FloatTensor(states).to(self.device)
        target_policies = torch.FloatTensor(target_policies).to(self.device)
        target_values = torch.FloatTensor(target_values).to(self.device)
        
        total_loss = 0
        num_batches = (len(states) + batch_size - 1) // batch_size
        
        for i in range(num_batches):
            start_idx = i * batch_size
            end_idx = min(start_idx + batch_size, len(states))
            
            batch_states = states[start_idx:end_idx]
            batch_policies = target_policies[start_idx:end_idx]
            batch_values = target_values[start_idx:end_idx]
            
            self.optimizer.zero_grad()
            policy_out, value_out = self.model(batch_states)
            
            policy_loss = -torch.mean(torch.sum(batch_policies * policy_out, dim=1))
            value_loss = torch.mean((value_out - batch_values) ** 2)
            loss = policy_loss + value_loss
            
            loss.backward()
            self.optimizer.step()
            total_loss += loss.item()
        
        return total_loss / num_batches
