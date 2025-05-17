# Minesweeper AI

This project implements the game of Minesweeper and an AI agent capable of playing it. The AI uses logical inference to deduce the locations of mines and safe cells on the board.

## Video Demo

[Project Demo Video](https://www.youtube.com/watch?v=KKIweTb6s1E&ab_channel=%E6%9D%B1%E9%A2%A8%E7%A5%9E) 

## Files

*   `minesweeper.py`: Contains all the core logic for the Minesweeper game itself, as well as the AI player. This includes:
    *   `Minesweeper` class: Manages the game board, mine placement, and game state.
    *   `Sentence` class: Represents a logical sentence about a set of cells and the number of mines within that set. It includes methods to identify known mines or safes within the sentence and to update the sentence based on new information.
    *   `MinesweeperAI` class: Implements the AI agent. It maintains a knowledge base of logical sentences and uses it to:
        *   Mark cells as safe or mines.
        *   Infer new safe cells and mines based on existing knowledge.
        *   Make safe moves or, if no safe move is known, random moves.
*   `runner.py`: Provides a graphical user interface (GUI) using Pygame to play the Minesweeper game. You can play the game manually or let the AI play.

## How to Run

1.  Ensure you have Python 3 installed.
2.  If you don't have Pygame installed, you might need to install it. Typically, this can be done via pip:
    ```bash
    pip install pygame
    ```
3.  Navigate to the project directory in your terminal.
4.  Run the game using the following command:
    ```bash
    python runner.py
    ```

## AI Logic Overview

The AI operates based on a knowledge base consisting of "sentences." Each sentence is a statement of the form "{cell1, cell2, ...} = count", meaning that out of the specified set of cells, exactly `count` of them are mines.

Key functionalities of the AI include:

1.  **`add_knowledge(cell, count)`**: When a safe cell is revealed along with the number of its neighboring mines (`count`), the AI:
    *   Marks the `cell` as a move made and as safe.
    *   Updates all existing sentences in its knowledge base that involve this `cell`.
    *   Forms a new sentence about the neighbors of `cell`. This sentence includes only neighbors whose states (mine or safe) are currently undetermined, and the count is adjusted for any neighboring cells already known to be mines.
    *   Repeatedly infers new information:
        *   If a sentence implies all its cells are mines (e.g., `{A, B} = 2`), those cells are marked as mines.
        *   If a sentence implies all its cells are safe (e.g., `{C, D} = 0`), those cells are marked as safe.
        *   If new mines or safes are identified, they are propagated through the knowledge base, potentially simplifying existing sentences or leading to further deductions.
        *   Uses a subset inference rule: If the AI knows `{A, B, C} = 2` (Sentence 1) and `{A, B} = 1` (Sentence 2), it can infer that `{C} = 1`. Such new sentences are added to the knowledge base.
    *   This process of inference continues iteratively until no new information can be derived.

2.  **`make_safe_move()`**: The AI iterates through all cells known to be safe and returns one that has not yet been clicked. If no such move exists, it returns `None`.

3.  **`make_random_move()`**: If no safe move can be identified, the AI will choose a random cell that has not yet been clicked and is not known to be a mine. If all remaining cells are either already clicked or known mines, it returns `None`.

This logical approach allows the AI to make intelligent decisions and solve Minesweeper puzzles. 
