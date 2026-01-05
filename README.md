# 🧩 Maze Solver & Creator – Python Project

## 📌 Project Description

This project focuses on designing, creating, and solving **2D grid-based mazes** using classical graph search algorithms.  
It combines an **interactive maze editor (GUI)** with an **animated maze solver**, allowing both manual maze creation and algorithmic exploration.

The project workflow is divided into the following stages:

1. **Maze creation phase:**  
   The user designs a maze using a graphical editor built with Tkinter. Walls, passages, start (`S`) and end (`E`) points can be placed interactively.  
  <img width="1133" height="983"
     alt="Maze Creator GUI"
     src="https://github.com/user-attachments/assets/b9ebf027-ebe4-486c-bcc5-e21b647da823" />


2. **Maze export phase:**  
   The created maze is saved to an ASCII text file using a simple and readable format (`#`, `.`, `S`, `E`).  
   <img width="393" height="797" alt="ASCII Maze File" src="https://github.com/user-attachments/assets/ed7efbcc-d83b-4992-a0aa-3fc35d00ca71" />
 />

3. **Solver execution phase:**  
   The maze is loaded into the solver, where one of the supported algorithms (BFS, DFS, or A*) is selected via command-line arguments or directly from the GUI.  
   alt="Solver CLI Execution showing maze loading and path length" <img width="758" height="73" src="https://github.com/user-attachments/assets/fbf1fe8c-2af3-44d9-abcb-7f3eea1c5721" />
 />
 />

4. **Exploration phase:**  
   The chosen algorithm explores the maze step by step. Visited cells are highlighted, allowing clear observation of the search strategy.  
 alt="Maze Exploration" <img width="895" height="916" src="https://github.com/user-attachments/assets/4176e302-000c-4461-8821-75fd32e9e56f" />
 />

5. **Final path visualization:**  
   Once the goal is reached, the final path from start to end is reconstructed and displayed, clearly distinguishing it from explored areas.  
   <img width="977" height="954" alt="Final Path Visualization" src="https://github.com/user-attachments/assets/5d098631-9257-456c-9010-60269a32f1d1" />

The project is implemented entirely in **Python**, combining GUI programming, algorithmic problem solving, and data visualization into a single coherent system.

---

## ⚙️ Technologies and Tools

- **Python 3.9+** – core programming language
- **Tkinter** – graphical user interface for maze creation
- **Matplotlib** – visualization and animation of maze-solving algorithms
- **NumPy** – efficient grid representation and state handling
- **argparse** – command-line interface for solver configuration

---

## 🧠 Implemented Algorithms

- **Breadth-First Search (BFS)**  
  Guarantees the shortest path in an unweighted maze.

- **Depth-First Search (DFS)**  
  Explores deeply before backtracking; does not guarantee the shortest path.

- **A\***  
  Uses the Manhattan distance heuristic to efficiently find the shortest path.

---

## 🧩 Features

- Interactive maze editor with real-time drawing
- Support for arbitrary maze sizes
- ASCII-based maze import and export
- Animated visualization of algorithm execution
- Clear distinction between walls, paths, visited cells, and final solution
- Optional random maze generation with loop control
- Modular and readable project structure

---

## 📄 ASCII Maze Format

```text
#########
#S..#...#
#.#.#.#.#
#.#...#.#
###.###.#
#...#..E#
#########
