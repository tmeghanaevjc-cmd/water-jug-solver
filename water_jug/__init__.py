"""Water Jug Problem solver using state-space search (BFS / DFS)."""

from .solver import Result, State, Step, WaterJugProblem, bfs, dfs, replay

__all__ = ["WaterJugProblem", "State", "Step", "Result", "bfs", "dfs", "replay"]
__version__ = "1.0.0"
