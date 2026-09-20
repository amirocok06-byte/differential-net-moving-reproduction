import torch

from dreamplace.paper_net_moving import endpoint_gradients_from_snapshot


def main():
    demand = torch.tensor([[2.0, 1.0, 1.0], [1.0, 1.0, 3.0]])
    capacity = torch.ones_like(demand)
    positions = torch.tensor([[0.2, 0.2], [2.2, 1.2], [1.2, 0.2]])
    pairs = torch.tensor([[0, 1], [1, 2]])
    out = endpoint_gradients_from_snapshot(
        positions, pairs, demand, capacity, torch.zeros(2), torch.ones(2), iterations=30
    )
    assert out["endpoint_gradients"].shape == (2, 2, 2)
    assert out["hotspots"].shape == (2, 2)
    assert torch.isfinite(out["endpoint_gradients"]).all()
    assert not out["endpoint_gradients"].requires_grad
    try:
        endpoint_gradients_from_snapshot(positions, torch.tensor([[0, 4]]), demand, capacity, torch.zeros(2), torch.ones(2))
    except ValueError:
        pass
    else:
        raise AssertionError("invalid pin id was accepted")
    print("paper net-moving snapshot test: PASS")


if __name__ == "__main__":
    main()
