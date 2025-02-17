# Jinxy Chess AI

<div align="center">
  <img src="1stVersion/images/logo.png" alt="Chess AI Logo" width="260" height="260" />
  <h3>A powerful neural network chess engine with advanced AI capabilities.</h3>
  <p><a href="#">Explore Jinxy Chess AI Docs »</a></p>

  <p>
    <a href="#">Report bug</a> ·
    <a href="#">Open a discussion</a> ·
    <a href="#">Discord</a> ·
    <a href="#">Blog</a>
  </p>

  <p>
    <img src="https://img.shields.io/badge/Jinxy%20AI-Passing-brightgreen" alt="Build Status"/>
    <img src="https://img.shields.io/badge/License-MIT-green" alt="License"/>
    <img src="https://img.shields.io/badge/Official%20Release-v1.0-blue" alt="Official Release"/>
    <img src="https://img.shields.io/badge/Commits-80%2B-blue" alt="Commits"/>
  </p>

  <p>
    <img src="https://img.shields.io/badge/Website-Offline-red" alt="Website"/>
    <img src="https://img.shields.io/badge/FishTest-Offline-red" alt="FishTest"/>
    <img src="https://img.shields.io/badge/Discord-Join-blue" alt="Discord"/>
    <img src="https://img.shields.io/badge/Stars-70-gold" alt="Users Online"/>
  </p>
</div>


## NOTE
this repository is only to read code purposes , after cloning u wont be able to play cuz there are some functionalities that i removed for the purpose of more development


## Overview
Welcome to the **Jinxy Chess AI Project**! This project integrates a sophisticated machine learning-based artificial intelligence (AI) with a user-friendly graphical user interface (GUI) built using Pygame. The goal is to provide an engaging and challenging chess-playing experience where users can compete against an AI opponent capable of making intelligent and strategic moves based on a trained neural network model 

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


- **`board.py`:**
  - Maintains the game state using the `Board` and `Move` classes.
  - Handles move generation, validation, and state updates.
  - Manages special moves like castling, en passant, and promotion.
  
- **`predict_move.py`:**
  - Interfaces with the neural network model to predict the best moves based on the current board state.
  - Converts FEN strings to numerical feature vectors suitable for the neural network.
  

- **`minimax.py`:**
  - Implements the Minimax algorithm as a fallback for move suggestions if the neural network does not provide a move.
  - Provides functions to evaluate board states and determine optimal moves.
  
- **`train_model.py`:**
  - Script for training the neural network model using training data from PGN files.
  - Handles data preprocessing, feature engineering, model training, and saving of trained models.
  
- **`data/`:**
  - Directory for storing training PGN (Portable Game Notation) files.
  - Collect a diverse set of chess games to train the AI effectively.

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


