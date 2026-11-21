"""Core model and search algorithms for the Water Jug Problem.

A *state* is the pair (a, b): litres currently in jug A and jug B.
A *move* is one of six legal operations (fill, empty, pour). The goal is any
state in which either jug holds exactly ``target`` litres.
"""

from __future__ import annotations

import math
import time
from collections import deque
from dataclasses import dataclass
from typing import Iterator, NamedTuple


class State(NamedTuple):
    """Amount of water (litres) in each jug."""

    a: int
    b: int


@dataclass(frozen=True)
class Step:
    """One entry of a solution path: the action taken and the state reached."""

    action: str
    state: State


@dataclass
class Result:
    """Outcome of a search run, including simple performance statistics."""

    strategy: str
    solvable: bool
    steps: list[Step]
    nodes_explored: int
    elapsed_ms: float
    reason: str = ""

    @property
    def moves(self) -> int:
        """Number of operations needed (the start state is not a move)."""
        return max(len(self.steps) - 1, 0)


class WaterJugProblem:
    """Two jugs with fixed capacities and a target quantity of water."""

    def __init__(self, cap_a: int, cap_b: int, target: int) -> None:
        for name, value in (("cap_a", cap_a), ("cap_b", cap_b), ("target", target)):
            if not isinstance(value, int) or isinstance(value, bool):
                raise TypeError(f"{name} must be an integer, got {value!r}")
        if cap_a <= 0 or cap_b <= 0:
            raise ValueError("Jug capacities must be positive integers.")
        if target < 0:
            raise ValueError("Target must not be negative.")
        self.cap_a, self.cap_b, self.target = cap_a, cap_b, target

    # ---- problem definition -------------------------------------------------
    @property
    def initial_state(self) -> State:
        return State(0, 0)

    def is_goal(self, state: State) -> bool:
        return state.a == self.target or state.b == self.target

    def successors(self, s: State) -> Iterator[tuple[str, State]]:
        """Yield every (action, next_state) reachable from ``s`` in one move."""
        pour_ab = min(s.a, self.cap_b - s.b)
        pour_ba = min(s.b, self.cap_a - s.a)
        candidates = (
            ("Fill Jug A", State(self.cap_a, s.b)),
            ("Fill Jug B", State(s.a, self.cap_b)),
            ("Empty Jug A", State(0, s.b)),
            ("Empty Jug B", State(s.a, 0)),
            ("Pour A -> B", State(s.a - pour_ab, s.b + pour_ab)),
            ("Pour B -> A", State(s.a + pour_ba, s.b - pour_ba)),
        )
        for action, nxt in candidates:
            if nxt != s:  # skip no-op moves
                yield action, nxt

    # ---- mathematical feasibility ------------------------------------------
    def is_solvable(self) -> bool:
        """Bezout's identity: reachable iff target <= max(cap) and gcd | target."""
        if self.target > max(self.cap_a, self.cap_b):
            return False
        return self.target % math.gcd(self.cap_a, self.cap_b) == 0

    def unsolvable_reason(self) -> str:
        if self.target > max(self.cap_a, self.cap_b):
            return (f"Target {self.target} exceeds the largest jug "
                    f"({max(self.cap_a, self.cap_b)}).")
        g = math.gcd(self.cap_a, self.cap_b)
        return (f"gcd({self.cap_a}, {self.cap_b}) = {g}, and {self.target} "
                f"is not a multiple of {g}.")


# ---- search ----------------------------------------------------------------
Parent = dict[State, "tuple[State, str] | None"]


def _build_path(parent: Parent, goal: State) -> list[Step]:
    path: list[Step] = []
    node: State | None = goal
    while node is not None:
        link = parent[node]
        path.append(Step("Start" if link is None else link[1], node))
        node = None if link is None else link[0]
    path.reverse()
    return path


def _finish(name: str, parent: Parent, goal: State | None,
            explored: int, t0: float) -> Result:
    elapsed = (time.perf_counter() - t0) * 1000
    if goal is None:
        return Result(name, False, [], explored, elapsed, "Search space exhausted.")
    return Result(name, True, _build_path(parent, goal), explored, elapsed)


def _unsolvable(name: str, problem: WaterJugProblem) -> Result:
    return Result(name, False, [], 0, 0.0, problem.unsolvable_reason())


def bfs(problem: WaterJugProblem) -> Result:
    """Breadth-first search: always returns a path with the fewest moves."""
    if not problem.is_solvable():
        return _unsolvable("BFS", problem)
    t0 = time.perf_counter()
    start = problem.initial_state
    parent: Parent = {start: None}
    queue: deque[State] = deque([start])
    explored = 0
    while queue:
        state = queue.popleft()
        explored += 1
        if problem.is_goal(state):
            return _finish("BFS", parent, state, explored, t0)
        for action, nxt in problem.successors(state):
            if nxt not in parent:
                parent[nxt] = (state, action)
                queue.append(nxt)
    return _finish("BFS", parent, None, explored, t0)


def dfs(problem: WaterJugProblem) -> Result:
    """Depth-first search (iterative): finds *a* path, not necessarily shortest."""
    if not problem.is_solvable():
        return _unsolvable("DFS", problem)
    t0 = time.perf_counter()
    start = problem.initial_state
    parent: Parent = {}
    stack: list[tuple[State, tuple[State, str] | None]] = [(start, None)]
    explored = 0
    while stack:
        state, link = stack.pop()
        if state in parent:
            continue
        parent[state] = link
        explored += 1
        if problem.is_goal(state):
            return _finish("DFS", parent, state, explored, t0)
        # reversed() so the first-listed move is explored first
        for action, nxt in reversed(list(problem.successors(state))):
            if nxt not in parent:
                stack.append((nxt, (state, action)))
    return _finish("DFS", parent, None, explored, t0)


def replay(problem: WaterJugProblem, steps: list[Step]) -> bool:
    """Independently verify that a solution path is legal and reaches the goal."""
    if not steps or steps[0].state != problem.initial_state:
        return False
    for prev, cur in zip(steps, steps[1:]):
        if (cur.action, cur.state) not in set(problem.successors(prev.state)):
            return False
    return problem.is_goal(steps[-1].state)
