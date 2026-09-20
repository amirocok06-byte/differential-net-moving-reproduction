import torch

from dreamplace.paper_congestion import congestion_map
from dreamplace.paper_two_pin_gradients import batch_two_pin_paper_formula_proxy


def main():
    demand = torch.ones(8, 8)
    demand[3, 4] = 3.0
    capacity = torch.ones_like(demand)
    c = congestion_map(demand, capacity)
    assert c[3, 4].item() == 2.0 and c.sum().item() == 2.0
    pins = torch.tensor([[0.5, 7.5], [3.5, 3.5]])
    pairs = torch.tensor([[0, 1]])
    gradients, hotspots = batch_two_pin_paper_formula_proxy(
        demand, capacity, pins, pairs, torch.zeros(2), torch.ones(2), poisson_iterations=40
    )
    assert gradients.shape == (1, 2, 2)
    assert hotspots.shape == (1, 2)
    assert torch.isfinite(gradients).all()
    print("paper formula global-map proxy test: PASS", tuple(hotspots[0].tolist()))


if __name__ == "__main__":
    main()
