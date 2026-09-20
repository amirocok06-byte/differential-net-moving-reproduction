import torch

from dreamplace.paper_two_pin_gradients import batch_two_pin_endpoint_gradients


def main():
    congestion = torch.zeros(5, 5)
    congestion[2, 3] = 4.0
    pins = torch.tensor([[0.5, 4.5, 0.5, 4.5], [2.5, 2.5, 0.5, 4.5]])
    pairs = torch.tensor([[0, 1], [2, 3]])
    gradients, hotspots = batch_two_pin_endpoint_gradients(
        congestion, pins, pairs, torch.zeros(2), torch.ones(2),
        poisson_iterations=30, samples_per_segment=16,
    )
    assert gradients.shape == (2, 2, 2)
    assert hotspots.shape == (2, 2)
    assert torch.isfinite(gradients).all()
    assert hotspots[0, 0].item() == 3
    try:
        batch_two_pin_endpoint_gradients(congestion, pins, pairs, torch.zeros(2), torch.ones(2), samples_per_segment=1)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid samples must be rejected")
    print("paper two-pin gradient batch test: PASS")


if __name__ == "__main__":
    main()
