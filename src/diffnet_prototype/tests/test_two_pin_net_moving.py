import torch

from dreamplace.two_pin_net_moving import (
    finite_difference_gradient,
    objective_and_gradient,
    two_pin_net_moving_objective,
    virtual_cell_position,
)


def test_virtual_cell_is_differentiable_midpoint():
    pins = torch.tensor([[1.0, 2.0], [5.0, 8.0]], requires_grad=True)
    target = torch.tensor([3.0, 5.0])
    assert torch.allclose(virtual_cell_position(pins), target)

    objective = two_pin_net_moving_objective(pins, target)
    objective.backward()
    assert torch.allclose(pins.grad, torch.zeros_like(pins))


def test_autograd_matches_finite_difference():
    pins = torch.tensor([[1.2, 2.4], [5.1, 7.7]], dtype=torch.double, requires_grad=True)
    target = torch.tensor([3.0, 4.5], dtype=torch.double)

    objective = two_pin_net_moving_objective(pins, target)
    objective.backward()
    numerical = finite_difference_gradient(pins, target)

    torch.testing.assert_close(pins.grad, numerical, rtol=1e-5, atol=1e-7)


def test_objective_and_gradient_matches_existing_objective():
    pins = torch.tensor(
        [[1.2, 2.4], [5.1, 7.7]], dtype=torch.double, requires_grad=True
    )
    target = torch.tensor([3.0, 4.5], dtype=torch.double)

    objective, gradient = objective_and_gradient(pins, target)
    expected = pins.detach().clone().requires_grad_(True)
    reference = two_pin_net_moving_objective(expected, target)
    (reference_gradient,) = torch.autograd.grad(reference, expected)

    torch.testing.assert_close(objective, reference)
    torch.testing.assert_close(gradient, reference_gradient)


def test_objective_and_gradient_respects_net_weight():
    pins = torch.tensor(
        [[1.0, 2.0], [5.0, 8.0]], dtype=torch.double, requires_grad=True
    )
    target = torch.tensor([3.0, 4.0], dtype=torch.double)

    objective, gradient = objective_and_gradient(pins, target, net_weight=0.0)

    assert objective.item() == 0.0
    torch.testing.assert_close(gradient, torch.zeros_like(pins))


def test_objective_and_gradient_accepts_external_congestion_loss():
    pins = torch.tensor(
        [[1.0, 2.0], [5.0, 8.0]], dtype=torch.double, requires_grad=True
    )
    target = torch.tensor([3.0, 4.0], dtype=torch.double)
    congestion = torch.tensor(2.5, dtype=torch.double)

    objective, gradient = objective_and_gradient(
        pins, target, congestion=congestion, congestion_weight=0.4
    )
    reference = two_pin_net_moving_objective(pins, target) + 0.4 * congestion

    torch.testing.assert_close(objective, reference)
    assert gradient.shape == pins.shape


def test_objective_and_gradient_rejects_non_scalar_congestion():
    pins = torch.tensor([[1.0, 2.0], [5.0, 8.0]], requires_grad=True)
    target = torch.tensor([3.0, 4.0])

    try:
        objective_and_gradient(pins, target, congestion=torch.ones(2))
    except ValueError as error:
        assert "scalar" in str(error)
    else:
        raise AssertionError("non-scalar congestion should be rejected")


def test_objective_and_gradient_handles_coincident_pins_and_float32():
    pins = torch.tensor([[2.0, 2.0], [2.0, 2.0]], requires_grad=True)
    target = torch.tensor([1.0, 1.0])

    objective, gradient = objective_and_gradient(pins, target)

    assert objective.dtype == torch.float32
    assert gradient.dtype == torch.float32
    assert torch.isfinite(objective)
    assert torch.isfinite(gradient).all()


if __name__ == "__main__":
    test_virtual_cell_is_differentiable_midpoint()
    test_autograd_matches_finite_difference()
    test_objective_and_gradient_matches_existing_objective()
    test_objective_and_gradient_respects_net_weight()
    print("two-pin net-moving gradient probe: PASS")
