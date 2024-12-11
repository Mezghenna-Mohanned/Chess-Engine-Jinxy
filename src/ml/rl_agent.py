import pygame
import torch
import torch.nn as nn
import torch.optim as optim
import random
from src.core.board import Board
from src.Ai.minimax import order_moves
from src.Ai.evaluation import evaluate
import numpy as np
from collections import deque
import matplotlib.pyplot as plt

class QNetwork(nn.Module):
    def __init__(self, input_size=832, hidden_sizes=[1024, 512], output_size=4672):
        super(QNetwork, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_sizes[0])
        self.relu1 = nn.ReLU()
        self.fc2 = nn.Linear(hidden_sizes[0], hidden_sizes[1])
        self.relu2 = nn.ReLU()
        self.output = nn.Linear(hidden_sizes[1], output_size)

    def forward(self, x):
        x = self.relu1(self.fc1(x))
        x = self.relu2(self.fc2(x))
        x = self.output(x)
        return x

class RLAgent:
    def __init__(self, learning_rate=0.001, gamma=0.99, epsilon_start=1.0, epsilon_end=0.1, epsilon_decay=0.995):
        self.q_network = QNetwork()
        self.target_network = QNetwork()
        self.update_target_network()
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=learning_rate)
        self.criterion = nn.MSELoss()
        self.gamma = gamma
        self.epsilon = epsilon_start  # Initial exploration rate
        self.epsilon_min = epsilon_end
        self.epsilon_decay = epsilon_decay
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.q_network.to(self.device)
        self.target_network.to(self.device)
        self.memory = deque(maxlen=50000)
        self.batch_size = 64
        self.learn_step_counter = 0
        self.target_update_frequency = 1000  # Update target network every 1000 steps

        # Metrics for monitoring training progress
        self.rewards_per_episode = []  # List to store total rewards per episode
        self.losses_per_episode = []   # List to store average losses per episode
        self.loss_list = []            # List to store losses during each episode

    def update_target_network(self):
        self.target_network.load_state_dict(self.q_network.state_dict())

    def board_to_tensor(self, board):
        feature = np.zeros((8, 8, 13), dtype=np.float32)
        piece_to_index = {
            'P': 0, 'N': 1, 'B': 2, 'R': 3, 'Q': 4, 'K': 5,
            'p': 6, 'n': 7, 'b': 8, 'r': 9, 'q': 10, 'k': 11
        }
        for square in range(64):
            piece = board.get_piece_at_square(square)
            if piece:
                row = 7 - (square // 8)
                col = square % 8
                piece_idx = piece_to_index[piece]
                feature[row, col, piece_idx] = 1
        active_color = 1 if board.white_to_move else 0
        feature[:, :, 12] = active_color
        return torch.tensor(feature.flatten(), dtype=torch.float32).to(self.device)

    def select_action(self, board, legal_moves):
        if random.random() < self.epsilon:
            # Exploration: choose a random move
            return random.choice(legal_moves)
        else:
            # Exploitation: choose the best move according to the Q-network
            board_tensor = self.board_to_tensor(board)
            q_values = self.q_network(board_tensor)
            move_indices = self.moves_to_indices(legal_moves)
            q_values = q_values[move_indices]
            max_q_index = torch.argmax(q_values).item()
            return legal_moves[max_q_index]

    def moves_to_indices(self, moves):
        """
        Maps a list of moves to indices in the Q-network output.
        """
        move_indices = []
        for move in moves:
            move_index = self.encode_move(move)
            move_indices.append(move_index)
        return torch.tensor(move_indices, dtype=torch.long).to(self.device)

    def encode_move(self, move):
        """
        Encodes a move into a unique index.
        """
        from_square = move.from_square
        to_square = move.to_square
        promotion_offset = 0
        if move.promoted_piece:
            promotion_dict = {'Q': 0, 'R': 1, 'B': 2, 'N': 3,
                              'q': 0, 'r': 1, 'b': 2, 'n': 3}
            promotion_offset = promotion_dict[move.promoted_piece] + 1
        # Unique index for each possible move (64*64*5)
        move_index = from_square * 64 * 5 + to_square * 5 + promotion_offset
        return move_index

    def store_transition(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def learn_from_memory(self):
        if len(self.memory) < self.batch_size:
            return
        batch = random.sample(self.memory, self.batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)

        state_tensors = torch.stack(states)
        next_state_tensors = torch.stack(next_states)
        action_indices = torch.tensor(actions, dtype=torch.long).to(self.device)
        rewards = torch.tensor(rewards, dtype=torch.float32).to(self.device)
        dones = torch.tensor(dones, dtype=torch.float32).to(self.device)

        q_values = self.q_network(state_tensors)
        q_values = q_values.gather(1, action_indices.unsqueeze(1)).squeeze(1)

        with torch.no_grad():
            next_q_values = self.target_network(next_state_tensors).max(1)[0]
            target_q_values = rewards + self.gamma * next_q_values * (1 - dones)

        loss = self.criterion(q_values, target_q_values)

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        self.learn_step_counter += 1
        if self.learn_step_counter % self.target_update_frequency == 0:
            self.update_target_network()

        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

        # Record the loss
        self.loss_list.append(loss.item())

    def calculate_reward(self, board, action, done):
        """
        Calculates the reward for a given board state and action.
        """
        reward = 0

        if done:
            if board.is_checkmate():
                if board.white_to_move:
                    reward = -1000  # Lose
                else:
                    reward = 1000   # Win
            else:
                reward = 0  # Draw
        else:
            # Use evaluation function as intermediate reward
            reward = evaluate(board)

        return reward

    def train(self, num_episodes=1000, gui=None):
        for episode in range(num_episodes):
            board = Board()
            state = self.board_to_tensor(board)
            total_reward = 0
            self.loss_list = []  # Reset loss list for the new episode
            done = False

            if gui:
                gui.board = board  # Set the board in GUI
                gui.running = True

            while not done:
                if gui:
                    gui.draw_board()
                    gui.draw_pieces()
                    pygame.display.flip()
                    pygame.event.pump()  # Process event queue

                legal_moves = board.generate_legal_moves()
                if not legal_moves:
                    # Game over
                    done = True
                    reward = self.calculate_reward(board, None, done)
                    total_reward += reward
                    self.store_transition(state, action_index, reward, state, done)
                    self.learn_from_memory()
                    break

                action = self.select_action(board, legal_moves)
                action_index = self.encode_move(action)
                board.make_move(action)
                next_state = self.board_to_tensor(board)
                done = board.is_game_over()
                reward = self.calculate_reward(board, action, done)
                total_reward += reward

                self.store_transition(state, action_index, reward, next_state, done)
                self.learn_from_memory()

                state = next_state

            # At the end of each episode, log the total reward and average loss
            avg_loss = np.mean(self.loss_list) if self.loss_list else 0
            self.rewards_per_episode.append(total_reward)
            self.losses_per_episode.append(avg_loss)

            # Display final statistics for the episode
            print(f"Episode {episode+1}/{num_episodes}")
            print(f"Total Reward: {total_reward}")
            print(f"Average Loss: {avg_loss:.4f}")
            print(f"Epsilon: {self.epsilon:.4f}")

            # Optionally, plot the progress after each episode (adjust frequency as needed)
            if (episode + 1) % 10 == 0:
                self.plot_progress()

        # After training, plot the overall training progress
        self.plot_progress(final=True)

    def plot_progress(self, final=False):
        episodes = range(1, len(self.rewards_per_episode) + 1)
        plt.figure(figsize=(12, 5))

        plt.subplot(1, 2, 1)
        plt.plot(episodes, self.rewards_per_episode, label='Total Reward per Episode')
        plt.xlabel('Episode')
        plt.ylabel('Total Reward')
        plt.title('Total Rewards Over Episodes')
        plt.legend()

        plt.subplot(1, 2, 2)
        plt.plot(episodes, self.losses_per_episode, label='Average Loss per Episode', color='orange')
        plt.xlabel('Episode')
        plt.ylabel('Average Loss')
        plt.title('Average Loss Over Episodes')
        plt.legend()

        plt.tight_layout()
        if final:
            plt.show()
        else:
            plt.pause(0.001)
            plt.clf()  # Clear the figure for the next update

    def save_model(self, path='models/rl_agent.pth'):
        torch.save(self.q_network.state_dict(), path)

    def load_model(self, path='models/rl_agent.pth'):
        self.q_network.load_state_dict(torch.load(path, map_location=self.device))
        self.q_network.to(self.device)
        self.update_target_network()

