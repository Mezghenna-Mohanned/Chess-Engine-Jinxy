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
        
        # Process in batches
        total_loss = 0
        for i in range(0, len(states), batch_size):
            batch_states = states[i:i+batch_size]
            batch_policies = target_policies[i:i+batch_size]
            batch_values = target_values[i:i+batch_size]
            
            self.optimizer.zero_grad()
            policy_out, value_out = self.model(batch_states)
            
            policy_loss = -torch.mean(torch.sum(batch_policies * policy_out, dim=1))
            value_loss = torch.mean((value_out - batch_values) ** 2)
            total_loss = policy_loss + value_loss
            
            total_loss.backward()
            self.optimizer.step()
        
        return total_loss.item()

    def train(self, train_loader, num_epochs):
        for epoch in range(num_epochs):
            total_loss = 0
            for batch_idx, (states, policies, values) in enumerate(train_loader):
                loss = self.train_step(states, policies, values)
                total_loss += loss
                
            print(f"Epoch {epoch+1}, Average Loss: {total_loss/len(train_loader)}")
