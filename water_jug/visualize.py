"""Terminal rendering and Graphviz export for solutions."""

from __future__ import annotations

from .solver import Result, State, WaterJugProblem


def bar(amount: int, capacity: int, width: int = 12) -> str:
    """Proportional fill bar, e.g. ██████░░░░░░."""
    filled = round(width * amount / capacity) if capacity else 0
    return "█" * filled + "░" * (width - filled)


def render_state(problem: WaterJugProblem, s: State) -> str:
    return (f"A [{bar(s.a, problem.cap_a)}] {s.a:>2}/{problem.cap_a:<2}   "
            f"B [{bar(s.b, problem.cap_b)}] {s.b:>2}/{problem.cap_b:<2}")


def render_result(problem: WaterJugProblem, result: Result) -> str:
    title = {"BFS": "BFS (shortest path guaranteed)",
             "DFS": "DFS (any valid path)"}.get(result.strategy, result.strategy)
    lines = [title, "-" * len(title)]
    if not result.solvable:
        lines.append(f"No solution: {result.reason}")
        return "\n".join(lines)
    for i, step in enumerate(result.steps):
        marker = "  <-- GOAL" if problem.is_goal(step.state) and i else ""
        lines.append(f"{i:>2}. {step.action:<12} ({step.state.a}, {step.state.b})  "
                     f"{render_state(problem, step.state)}{marker}")
    lines.append(f"\n{result.moves} moves | {result.nodes_explored} states explored "
                 f"| {result.elapsed_ms:.3f} ms")
    return "\n".join(lines)


def to_dot(problem: WaterJugProblem, result: Result | None = None) -> str:
    """Export the full reachable state-space graph as Graphviz DOT.

    The solution path (if given) is highlighted in red.
    Render with:  dot -Tpng state_space.dot -o state_space.png
    """
    on_path = set()
    if result and result.solvable:
        on_path = {(p.state, c.state) for p, c in zip(result.steps, result.steps[1:])}
    seen = {problem.initial_state}
    todo = [problem.initial_state]
    edges: list[tuple[State, State, str]] = []
    while todo:
        s = todo.pop()
        for action, nxt in problem.successors(s):
            edges.append((s, nxt, action))
            if nxt not in seen:
                seen.add(nxt)
                todo.append(nxt)
    out = ["digraph WaterJug {", "  rankdir=LR; node [shape=circle, fontsize=10];"]
    for s in sorted(seen):
        style = ' style=filled fillcolor="#b6f2c1"' if problem.is_goal(s) else ""
        out.append(f'  "{s.a},{s.b}" [label="({s.a},{s.b})"{style}];')
    for s, n, action in edges:
        hot = (s, n) in on_path
        attrs = f'label="{action}" fontsize=8' + (' color=red penwidth=2' if hot else "")
        out.append(f'  "{s.a},{s.b}" -> "{n.a},{n.b}" [{attrs}];')
    out.append("}")
    return "\n".join(out)
