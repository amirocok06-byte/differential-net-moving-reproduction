import torch

from dreamplace.net_moving_callback import make_two_pin_objective_from_congestion_snapshot


def main():
    pairs = torch.tensor([[0, 1], [2, 3]])
    flat = torch.tensor([0, 1, 2, 3])
    starts = torch.tensor([0, 2, 4])
    pos = torch.tensor([0.5, 3.5, 0.5, 3.5, 0.5, 0.5, 3.5, 3.5], requires_grad=True)
    pin_pos_op = lambda value: value.view(2, 4)
    congestion = torch.zeros(4, 4)
    congestion[1, 2] = 3.0
    callback, endpoint, hotspots = make_two_pin_objective_from_congestion_snapshot(
        pin_pos_op, pos.detach().view(2, 4), flat, starts, congestion,
        torch.zeros(2), torch.ones(2), poisson_iterations=10, samples_per_segment=8
    )
    assert endpoint.shape == (2, 2, 2)
    assert hotspots.shape == (2, 2)
    base = (pos ** 2).sum()
    base.backward()
    default_grad = pos.grad.detach().clone()
    pos.grad = None
    enabled = base.detach().clone().requires_grad_(True) + callback(pos)
    enabled.backward()
    assert torch.isfinite(pos.grad).all()
    assert not torch.allclose(pos.grad, default_grad)
    with torch.no_grad():
        pos -= 1e-3 * pos.grad
    assert torch.isfinite(pos).all()
    print("callback CPU 1-iteration smoke: PASS")


if __name__ == "__main__":
    main()
