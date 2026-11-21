# Water Jug Problem Solver

A clean, tested Python implementation of the classic **Water Jug Problem** using
**state-space search**. Given two jugs with fixed capacities and a target quantity,
the program finds and displays the exact sequence of operations that measures the
target, using **Breadth-First Search (BFS)** and **Depth-First Search (DFS)**.

- Pure Python 3.9+, **no external dependencies** (pytest only for tests)
- BFS returns the **provably shortest** solution; DFS shown for comparison
- Detects **unsolvable** inputs instantly using number theory (Bezout / GCD)
- Every solution is **independently verified** by a replay checker
- Optional **Graphviz export** of the full state-space graph with the solution highlighted

## Problem modelling

| Concept | Representation |
|---|---|
| State | `(a, b)` = litres in jug A and jug B, with `0 <= a <= cap_a`, `0 <= b <= cap_b` |
| Initial state | `(0, 0)` |
| Goal test | `a == target` or `b == target` |
| Operators | Fill A, Fill B, Empty A, Empty B, Pour A->B, Pour B->A |
| Pour rule | `amount = min(source, capacity_destination - destination)` |
| Search space size | at most `(cap_a + 1) * (cap_b + 1)` states |

## Algorithms

| | BFS | DFS |
|---|---|---|
| Data structure | FIFO queue | LIFO stack |
| Shortest solution | **Yes** | No |
| Time | O(cap_a x cap_b) | O(cap_a x cap_b) |
| Space | O(cap_a x cap_b) | O(cap_a x cap_b) |

Both keep a `visited`/`parent` map, so each state is expanded once and the path is
rebuilt by following parent links back from the goal.

**Solvability (Bezout's identity):** a target `t` can be measured if and only if
`t <= max(cap_a, cap_b)` and `gcd(cap_a, cap_b)` divides `t`. For example, jugs of 2 L
and 4 L can never measure 3 L. The test-suite checks this rule against brute-force
reachability for hundreds of small instances.

## Usage

```bash
# default example: jugs 4 L and 3 L, target 2 L, run both BFS and DFS
python -m water_jug

# custom input
python -m water_jug --a 5 --b 3 --target 4 --strategy bfs

# export state-space graph (red edges = solution path)
python -m water_jug --a 4 --b 3 --target 2 --dot state_space.dot
dot -Tpng state_space.dot -o state_space.png     # needs Graphviz
```

Exit codes: `0` solved, `1` no solution exists, `2` invalid input.

### Sample output

```
BFS (shortest path guaranteed)
------------------------------
 0. Start        (0, 0)  A [░░░░░░░░░░░░]  0/4    B [░░░░░░░░░░░░]  0/3
 1. Fill Jug B   (0, 3)  A [░░░░░░░░░░░░]  0/4    B [████████████]  3/3
 2. Pour B -> A  (3, 0)  A [█████████░░░]  3/4    B [░░░░░░░░░░░░]  0/3
 3. Fill Jug B   (3, 3)  A [█████████░░░]  3/4    B [████████████]  3/3
 4. Pour B -> A  (4, 2)  A [████████████]  4/4    B [████████░░░░]  2/3   <-- GOAL

4 moves | 10 states explored
```

DFS finds a valid but longer 6-move path for the same input, which shows why BFS is
the right choice when the fewest steps matter.

## Use as a library

```python
from water_jug import WaterJugProblem, bfs

problem = WaterJugProblem(cap_a=5, cap_b=3, target=4)
result = bfs(problem)
for step in result.steps:
    print(step.action, step.state)
```

## Project structure

```
water-jug-solver/
├── water_jug/
│   ├── solver.py      # problem model, BFS, DFS, solution verifier
│   ├── visualize.py   # terminal rendering + Graphviz export
│   └── __main__.py    # command-line interface
├── tests/test_solver.py
├── requirements.txt
└── README.md
```

## Tests

```bash
pip install pytest
python -m pytest -q
```

Covers optimality of BFS, validity of DFS paths, unsolvable detection, the GCD rule
vs. exhaustive search, capacity invariants, tamper detection in the verifier,
input validation and CLI exit codes.

## Author

Tammana Bala Meghana
