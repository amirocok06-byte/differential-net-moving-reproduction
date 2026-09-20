"""Synthetic tests for the isolated Poisson congestion probe."""

import torch

from dreamplace.poisson_congestion_probe import potential_gradient, solve_poisson_jacobi


def test_constant_congestion_has_zero_source_solution():
    congestion = torch.ones((5, 7), dtype=torch.double)
    phi = solve_poisson_jacobi(congestion, iterations=20)
    torch.testing.assert_close(phi, torch.zeros_like(phi))


def test_solution_and_gradient_shapes_and_boundaries():
    source = torch.zeros((7, 7), dtype=torch.double)
    source[3, 3] = 1.0
    phi = solve_poisson_jacobi(source, iterations=300)
    assert phi.shape == source.shape
    torch.testing.assert_close(phi[0, :], torch.zeros(7, dtype=torch.double))
    torch.testing.assert_close(phi[-1, :], torch.zeros(7, dtype=torch.double))
    gx, gy = potential_gradient(phi, torch.tensor([2.0, 4.0], dtype=torch.double))
    assert gx.shape == source.shape and gy.shape == source.shape
    assert torch.isfinite(gx).all() and torch.isfinite(gy).all()


def test_invalid_inputs_are_rejected():
    try:
        solve_poisson_jacobi(torch.zeros((2, 3)))
    except ValueError:
        pass
    else:
        raise AssertionError("expected shape validation")
    try:
        potential_gradient(torch.zeros((3, 3)), torch.tensor([1.0, 0.0]))
    except ValueError:
        pass
    else:
        raise AssertionError("expected grid-size validation")


if __name__ == "__main__":
    test_constant_congestion_has_zero_source_solution()
    test_solution_and_gradient_shapes_and_boundaries()
    test_invalid_inputs_are_rejected()
    print("Poisson congestion probe test: PASS")
