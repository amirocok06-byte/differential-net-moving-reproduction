import torch

from dreamplace.net_moving_callback import (
    make_two_pin_objective,
    make_two_pin_objective_from_flat_map,
    make_two_pin_objective_from_congestion_snapshot,
)


def main():
    pairs = torch.tensor([[0, 1], [2, 3]])
    endpoint = torch.tensor([
        [[1.0, 2.0], [3.0, 4.0]],
        [[-1.0, 0.5], [2.0, -2.0]],
    ])

    def pin_pos_op(pos):
        # Four pins, each attached to one scalar x/y position in this probe.
        return pos.view(2, 4)

    pos = torch.tensor([10.0, 20.0, 30.0, 40.0, 1.0, 2.0, 3.0, 4.0], requires_grad=True)
    objective = make_two_pin_objective(pin_pos_op, pairs, endpoint)
    value = objective(pos)
    value.backward()
    expected = torch.tensor([1.0, 3.0, -1.0, 2.0, 2.0, 4.0, 0.5, -2.0])
    assert torch.allclose(pos.grad, expected)
    assert torch.allclose(value, (pos.detach() * expected).sum())
    flat = torch.tensor([0, 1, 2, 3, 4])
    starts = torch.tensor([0, 2, 5])
    zero_endpoint = torch.zeros(1, 2, 2)
    zero_objective = make_two_pin_objective_from_flat_map(
        pin_pos_op, flat, starts, zero_endpoint
    )
    pos.grad = None
    assert torch.equal(zero_objective(pos), torch.tensor(0.0))
    zero_objective(pos).backward()
    assert torch.equal(pos.grad, torch.zeros_like(pos))
    congestion = torch.zeros(5, 5)
    congestion[2, 3] = 4.0
    snapshot_objective, endpoint, hotspots = make_two_pin_objective_from_congestion_snapshot(
        pin_pos_op, pos.detach().view(2, 4), flat, starts, congestion,
        torch.zeros(2), torch.ones(2), poisson_iterations=30, samples_per_segment=16
    )
    assert endpoint.shape == (1, 2, 2)
    assert hotspots.shape == (1, 2)
    pos.grad = None
    snapshot_objective(pos).backward()
    assert torch.isfinite(pos.grad).all()
    print("two-pin net-moving callback test: PASS")


if __name__ == "__main__":
    main()
