import torch

from dreamplace.paper_two_pin_gradients import batch_two_pin_paper_formula_proxy


def main():
    demand = torch.ones(8, 8)
    demand[3, 4] = 3.0
    capacity = torch.ones_like(demand)
    pins = torch.tensor([[0.5, 7.5], [3.5, 3.5]])
    pairs = torch.tensor([[0, 1]])
    gradients, hotspots, trace = batch_two_pin_paper_formula_proxy(
        demand, capacity, pins, pairs, torch.zeros(2), torch.ones(2),
        poisson_iterations=40, return_trace=True
    )
    assert gradients.shape == (1, 2, 2)
    assert hotspots.shape == (1, 2)
    assert trace["virtual_cell"].shape == (1, 2)
    assert trace["raw_gradient"].shape == (1, 2)
    assert trace["projected_gradient"].shape == (1, 2)
    length = trace["segment_length"][0]
    assert torch.allclose(
        gradients[0, 0], length / (2 * trace["div_start"][0]) * trace["projected_gradient"][0]
    )
    assert torch.allclose(
        gradients[0, 1], length / (2 * trace["div_end"][0]) * trace["projected_gradient"][0]
    )
    assert torch.isfinite(torch.cat([gradients.reshape(-1), trace["virtual_cell"].reshape(-1)])).all()
    print("paper formula trace test: PASS")


if __name__ == "__main__":
    main()
