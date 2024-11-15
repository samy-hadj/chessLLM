# ChessLLM: Chess Game Assistant Powered by an LLM

### Project Members
- **Briac Six**
- **Jason Perez**
- **Samy Hadj-said**

### Project Overview
ChessLLM is a research project exploring the use of a language model (GPT-like) to analyze chess games and suggest optimal moves. Unlike traditional chess engines that rely on brute-force search, ChessLLM leverages the pattern recognition abilities of language models to understand strategies embedded in millions of historical games.

### Objectives
- **Understanding Chess Rules**: Train the model to avoid illegal moves while promoting winning strategies.
- **Training on Historical Games**: Utilize PGN-formatted game data to train the model on quality move sequences.
- **Interactive Interface**: Build a real-time chessboard interface that allows users to receive move recommendations interactively.

### Features
- **Data Preprocessing**: Extract and format move sequences from PGN files.
- **Training a GPT Model**: Fine-tune on chess game sequences to provide move recommendations.
- **Interactive Web Interface**: Display a chessboard with real-time move suggestions for interactive learning.

### Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/samy-hadj/chessLLM.git
cd chessLLM
```

### Usage
1. Run the training script to train the model on chess games.
2. Launch the interactive interface to play and receive move suggestions.

### Preliminary Results
The current model, based on GPT-2, has shown promising performance after initial training sessions. Expanding the dataset is planned to improve the accuracy and quality of suggested moves.

### Contributions
Contributions are welcome! Please submit a pull request or report issues in the relevant sections.