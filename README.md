# ChessLLM: Chess Game Assistant Powered by an LLM

### Project Members
- **Briac Six**  
- **Jason Perez**  
- **Samy Hadj-said**  

---

## Project Overview  
ChessLLM is an assistant powered by an advanced language model (GPT-like) designed to analyze chess games and suggest optimal moves. Unlike traditional chess engines that rely on brute-force search, ChessLLM leverages the pattern recognition capabilities of language models to understand strategies embedded in millions of historical games.  

---

## Objectives  
- **Understanding Chess Rules**: Ensure the model avoids illegal moves while promoting winning strategies.  
- **Training on Historical Games**: Train the model on PGN-formatted game data to learn high-quality move sequences.  
- **Interactive Interface**: Create a real-time chessboard interface that provides move recommendations interactively.  

---

## Project Structure  
The repository is organized as follows:  

```
assets/                     # Static assets (images, icons, etc.)
interface/                  # Code for the interactive chessboard
.gitignore                  # Files and directories to ignore in version control
ChessLLM.ipynb              # Main notebook for exploratory development
README.md                   # Project documentation
Rapport.pdf                 # Project report in PDF format
chess-llm.ipynb             # Notebook for testing and deploying the model
data_visualisation.ipynb    # Notebook for visualizing training data
entrainement.ipynb          # Notebook for training the model
pyproject.toml              # Dependency and configuration file for Python tools
rapport.tex                 # LaTeX source file for the project report
uv.lock                     # Dependency lock file
```  

---

## Implementation Details  
### 1. **Data Preprocessing**  
   PGN (Portable Game Notation) files are parsed and formatted to extract structured move sequences. These sequences serve as the training data for the model.  

### 2. **Model Training**  
   - Fine-tune a GPT-based model on the processed chess data.  
   - Use transfer learning to leverage pre-trained language model capabilities, enhancing performance on chess-specific tasks.  

### 3. **Interactive Interface**  
   A web-based chessboard interface is implemented to:  
   - Display real-time move suggestions.  
   - Allow users to play against the AI or analyze historical games.  

---

## Running the ChessLLM Interface

To execute the interactive chessboard interface, follow these steps:

### 1. **Place the model in models/best_model**  

### 2. **Navigate to the Interface Directory**  
   Open your terminal and navigate to the `interface/src/` directory:
   ```bash
   cd path/to/chessLLM/interface/src/
   ```

### 3. **Install Dependencies Using `uv.lock`**  
   ChessLLM uses `uv.lock` for managing dependencies. To install all the required dependencies, run the following command in the root of your project directory (where `uv.lock` is located):
   ```bash
   uv sync
   ```
   This will install all the necessary dependencies specified in `uv.lock`.

### 4. **Run the Interface**  
   Once the dependencies are installed, execute the `main.py` script to launch the chessboard:
   ```bash
   python main.py
   ```

### 5. **Interacting with the Interface**  
   - The chessboard will open, allowing you to play a game and receive move suggestions.
   - Moves will be logged in PGN format for analysis.