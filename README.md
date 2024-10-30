# Chess AI Project

![Chess AI Logo](images/logo.png)

Welcome to the **Chess AI Project**! This project integrates a sophisticated machine learning-based artificial intelligence (AI) with a user-friendly graphical user interface (GUI) built using Pygame. The goal is to provide an engaging and challenging chess-playing experience where users can compete against an AI opponent capable of making intelligent and strategic moves based on a trained neural network model.

---

## Table of Contents

1. [Introduction](#introduction)
2. [Features](#features)
3. [Project Structure](#project-structure)
4. [Installation](#installation)
    - [Prerequisites](#prerequisites)
    - [Clone the Repository](#clone-the-repository)
    - [Set Up Virtual Environment](#set-up-virtual-environment)
    - [Install Dependencies](#install-dependencies)
5. [Usage](#usage)
    - [Running the Application](#running-the-application)
    - [Gameplay Instructions](#gameplay-instructions)
6. [Training the AI Model](#training-the-ai-model)
    - [Data Preparation](#data-preparation)
    - [Feature Engineering](#feature-engineering)
    - [Neural Network Architecture](#neural-network-architecture)
    - [Training Process](#training-process)
    - [Saving and Loading Models](#saving-and-loading-models)
7. [Customization](#customization)
    - [Changing Board Themes](#changing-board-themes)
    - [Custom Piece Images](#custom-piece-images)
    - [Adjusting AI Difficulty](#adjusting-ai-difficulty)
8. [Troubleshooting](#troubleshooting)
    - [Common Errors](#common-errors)
    - [Debugging Tips](#debugging-tips)
9. [Contributing](#contributing)
10. [License](#license)
11. [Acknowledgments](#acknowledgments)
12. [Future Enhancements](#future-enhancements)

---

## Introduction

Chess has been a cornerstone in the development of artificial intelligence, serving as a benchmark for testing AI capabilities in strategic thinking and decision-making. The **Chess AI Project** aims to merge the strategic depth of chess with modern AI techniques, creating an AI opponent that can challenge players of varying skill levels.

This project leverages a neural network trained on extensive chess game data to predict and execute moves. The integration with Pygame ensures that users have a seamless and interactive experience, allowing them to focus on the game without being bogged down by technical complexities.

Whether you're a chess enthusiast eager to test your skills against an AI or a developer interested in the intersection of game development and machine learning, this project offers valuable insights and a robust platform for exploration.

---

## Features

- **Interactive GUI:**
  - Visually appealing chessboard rendered using Pygame.
  - Real-time move highlighting for selected pieces and valid destinations.
  - Smooth animations for piece movements and special actions.

- **AI Opponent:**
  - Utilizes a neural network model trained on diverse chess game data.
  - Capable of predicting and executing intelligent moves based on the current board state.
  - Adjustable difficulty levels to cater to players of different skill sets.

- **Move Validation:**
  - Comprehensive validation ensuring adherence to official chess rules.
  - Supports all standard moves, including castling, en passant, and pawn promotion.
  - Prevents illegal moves and provides feedback to the user.

- **Game State Management:**
  - Maintains accurate game state using FEN (Forsyth-Edwards Notation).
  - Detects game-ending conditions such as checkmate, stalemate, threefold repetition, and the fifty-move rule.
  - Provides options to restart the game or exit upon conclusion.

- **Move History:**
  - Logs all moves made during the game for reference and analysis.
  - Displays move history within the GUI for easy access.

- **Promotion Handling:**
  - Prompts users to choose a piece upon pawn promotion.
  - Ensures that promotions are executed smoothly without disrupting gameplay.

- **Customization:**
  - Ability to change board colors and piece styles.
  - Support for different image sets to personalize the gaming experience.

- **Performance Optimization:**
  - Efficient neural network architecture for quick move predictions.
  - Utilizes CPU or GPU resources based on availability for enhanced performance.

---

### File and Directory Descriptions

- **`GUI.py`:**
  - Manages the graphical user interface.
  - Handles user interactions, rendering of the chessboard and pieces, move selection, and integration with the AI for move suggestions.
  
- **`board.py`:**
  - Maintains the game state using the `Board` and `Move` classes.
  - Handles move generation, validation, and state updates.
  - Manages special moves like castling, en passant, and promotion.
  
- **`predict_move.py`:**
  - Interfaces with the neural network model to predict the best moves based on the current board state.
  - Converts FEN strings to numerical feature vectors suitable for the neural network.
  
- **`utils.py`:**
  - Contains utility functions for converting between different representations.
  - Includes functions like `algebraic_to_square` and `square_to_algebraic` for handling move notations.
  
- **`minimax.py`:**
  - Implements the Minimax algorithm as a fallback for move suggestions if the neural network does not provide a move.
  - Provides functions to evaluate board states and determine optimal moves.
  
- **`train_model.py`:**
  - Script for training the neural network model using training data from PGN files.
  - Handles data preprocessing, feature engineering, model training, and saving of trained models.
  
- **`models/`:**
  - **`best_move_model.pth`**: The trained PyTorch model weights. This file is essential for the AI to function.
  - **`labels_mapping.json`**: JSON file mapping move indices to UCI move strings and vice versa. It ensures that the model's outputs can be translated into valid chess moves.
  
- **`images/`:**
  - Contains images for all chess pieces and the project logo.
  - Ensure that the image filenames correspond to the expected naming conventions in the `load_images` function within `GUI.py`.
  
- **`data/`:**
  - Directory for storing training PGN (Portable Game Notation) files.
  - Collect a diverse set of chess games to train the AI effectively.
  
- **`requirements.txt`:**
  - Lists all Python dependencies required to run the project.
  - Facilitates easy installation of dependencies using `pip`.
  
- **`README.md`:**
  - This documentation file providing comprehensive information about the project.
  
- **`LICENSE`:**
  - Contains the licensing information for the project. The current project uses the MIT License.

---

## Installation

Setting up the Chess AI Project involves several steps, including installing necessary dependencies, setting up a virtual environment, and ensuring that all required assets are in place.

### Prerequisites

Before diving into the installation, ensure that your system meets the following prerequisites:

- **Operating System:**
  - Windows 10 or higher
  - macOS Catalina or higher
  - Linux (Ubuntu 18.04 or higher recommended)
  
- **Python Version:**
  - Python 3.7 or higher
  - Download Python from [python.org](https://www.python.org/downloads/)

- **Git:**
  - For cloning the repository
  - Download Git from [git-scm.com](https://git-scm.com/downloads)

- **Hardware:**
  - **CPU:** Modern processor
  - **GPU (Optional):** For accelerated neural network training and inference using PyTorch

### Clone the Repository

Start by cloning the repository to your local machine using Git.

```bash
git clone https://github.com/yourusername/ChessAI.git
cd ChessAI
