import pytest

from water_jug import WaterJugProblem, State, Step, bfs, dfs, replay
from water_jug.__main__ import main


@pytest.mark.parametrize("a,b,t,optimal", [(4, 3, 2, 4), (3, 5, 4, 6), (5, 3, 4, 6),
                                            (7, 4, 5, 8), (1, 1, 1, 1)])
def test_bfs_is_valid_and_optimal(a, b, t, optimal):
    p = WaterJugProblem(a, b, t)
    r = bfs(p)
    assert r.solvable and replay(p, r.steps)
    assert r.moves == optimal


def test_dfs_valid_and_never_shorter_than_bfs():
    for a, b, t in [(4, 3, 2), (3, 5, 4), (7, 4, 5), (9, 6, 3)]:
        p = WaterJugProblem(a, b, t)
        d, b_ = dfs(p), bfs(p)
        assert d.solvable and replay(p, d.steps)
        assert d.moves >= b_.moves


def test_target_zero_needs_no_moves():
    r = bfs(WaterJugProblem(4, 3, 0))
    assert r.solvable and r.moves == 0


@pytest.mark.parametrize("a,b,t", [(2, 4, 3), (6, 9, 4), (3, 5, 6)])
def test_unsolvable_detected_with_reason(a, b, t):
    p = WaterJugProblem(a, b, t)
    assert not p.is_solvable()
    for solve in (bfs, dfs):
        r = solve(p)
        assert not r.solvable and r.reason


def test_math_check_agrees_with_exhaustive_search():
    """gcd rule must match brute-force reachability for every small instance."""
    for a in range(1, 8):
        for b in range(1, 8):
            for t in range(0, 10):
                p = WaterJugProblem(a, b, t)
                seen, todo = {p.initial_state}, [p.initial_state]
                while todo:
                    for _, n in p.successors(todo.pop()):
                        if n not in seen:
                            seen.add(n)
                            todo.append(n)
                assert p.is_solvable() == any(p.is_goal(s) for s in seen), (a, b, t)


def test_no_state_exceeds_capacity():
    p = WaterJugProblem(5, 3, 4)
    for step in bfs(p).steps:
        assert 0 <= step.state.a <= 5 and 0 <= step.state.b <= 3


def test_replay_rejects_tampered_path():
    p = WaterJugProblem(4, 3, 2)
    steps = bfs(p).steps
    steps[2] = Step(steps[2].action, State(4, 0))
    assert not replay(p, steps)


@pytest.mark.parametrize("args", [(0, 3, 1), (4, -1, 1), (4, 3, -2)])
def test_invalid_input_rejected(args):
    with pytest.raises(ValueError):
        WaterJugProblem(*args)


def test_non_integer_rejected():
    with pytest.raises(TypeError):
        WaterJugProblem(4.5, 3, 2)


def test_cli_exit_codes(tmp_path):
    assert main(["--a", "4", "--b", "3", "--target", "2"]) == 0
    assert main(["--a", "2", "--b", "4", "--target", "3"]) == 1
    assert main(["--a", "0"]) == 2
    out = tmp_path / "g.dot"
    assert main(["--dot", str(out)]) == 0
    assert out.read_text().startswith("digraph")
