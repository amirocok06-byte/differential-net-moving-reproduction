import torch

from dreamplace.paper_congestion import (
    congestion_map,
    lambda2_from_gradients,
    poisson_source,
    potential_gradient_neumann,
    solve_poisson_neumann_jacobi,
)


def main():
    demand = torch.tensor([[1.0, 2.0], [4.0, 1.0]])
    capacity = torch.ones_like(demand) * 2
    assert torch.equal(congestion_map(demand, capacity), torch.tensor([[0.0, 0.0], [1.0, 0.0]]))
    source = poisson_source(demand, capacity)
    assert torch.allclose(source.mean(), torch.tensor(0.0))
    phi = solve_poisson_neumann_jacobi(source, torch.tensor([1.0, 1.0]), 40)
    gx, gy = potential_gradient_neumann(phi, torch.tensor([1.0, 1.0]))
    assert phi.shape == source.shape and torch.isfinite(phi).all()
    assert gx[:, 0].abs().max() == 0 and gx[:, -1].abs().max() == 0
    assert gy[0, :].abs().max() == 0 and gy[-1, :].abs().max() == 0
    value = lambda2_from_gradients(torch.ones(4), torch.ones(4) * 2, 3, 10)
    assert torch.allclose(value, torch.tensor(0.3))
    print("paper congestion definitions test: PASS")


if __name__ == "__main__":
    main()
