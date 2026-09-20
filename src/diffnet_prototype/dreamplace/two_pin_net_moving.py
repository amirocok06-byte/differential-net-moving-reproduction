"""Minimal differentiable two-pin net-moving probe.

This module is intentionally independent from the DREAMPlace placer.  It gives
the research branch a small, testable interface before integration into
PlaceObj/NonLinearPlace.
"""

import torch
from typing import Optional


def virtual_cell_position(pin_pos: torch.Tensor) -> torch.Tensor:
    """Return the differentiable virtual-cell position of a two-pin net.

    Args:
        pin_pos: Tensor with shape ``(2, 2)``: ``[[x0, y0], [x1, y1]]``.
    """
    if pin_pos.shape != (2, 2):
        raise ValueError("pin_pos must have shape (2, 2)")
    return pin_pos.mean(dim=0)


def two_pin_net_moving_objective(
    pin_pos: torch.Tensor, target: torch.Tensor
) -> torch.Tensor:
    """Squared distance from pins to a target virtual-cell location.

    The virtual cell is the mean of the two pins.  This objective is a small
    differentiable proxy for testing the proposed net-moving data path; it is
    not claimed to replace DREAMPlace's wirelength objective.
    """
    if target.shape != (2,):
        raise ValueError("target must have shape (2,)")
    virtual_cell = virtual_cell_position(pin_pos)
    return ((virtual_cell - target) ** 2).sum()


def objective_and_gradient(
    pin_pos: torch.Tensor,
    target: torch.Tensor,
    net_weight: float = 1.0,
    congestion: Optional[torch.Tensor] = None,
    congestion_weight: float = 0.0,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Return the proxy objective and its gradient with respect to ``pin_pos``.

    ``congestion`` is an externally computed scalar loss.  This probe does
    not define how congestion is computed; it only exposes the weighting
    interface needed for a later paper-faithful implementation.
    """
    if net_weight < 0:
        raise ValueError("net_weight must be non-negative")
    if congestion_weight < 0:
        raise ValueError("congestion_weight must be non-negative")
    if not pin_pos.is_floating_point():
        raise TypeError("pin_pos must be a floating-point tensor")
    if not target.is_floating_point():
        raise TypeError("target must be a floating-point tensor")
    if congestion is not None:
        if not isinstance(congestion, torch.Tensor):
            raise TypeError("congestion must be a scalar tensor or None")
        if congestion.ndim != 0:
            raise ValueError("congestion must be a scalar tensor")
        if not congestion.is_floating_point():
            raise TypeError("congestion must be a floating-point tensor")
        if congestion.device != pin_pos.device or congestion.dtype != pin_pos.dtype:
            raise TypeError("congestion must match pin_pos device and dtype")

    objective = net_weight * two_pin_net_moving_objective(pin_pos, target)
    if congestion is not None:
        objective = objective + congestion_weight * congestion
    (gradient,) = torch.autograd.grad(
        objective,
        pin_pos,
        create_graph=torch.is_grad_enabled(),
        retain_graph=False,
    )
    return objective, gradient


def finite_difference_gradient(
    pin_pos: torch.Tensor, target: torch.Tensor, epsilon: float = 1e-4
) -> torch.Tensor:
    """Compute a central-difference gradient without autograd."""
    numerical = torch.zeros_like(pin_pos)
    for i in range(pin_pos.shape[0]):
        for j in range(pin_pos.shape[1]):
            plus = pin_pos.detach().clone()
            minus = pin_pos.detach().clone()
            plus[i, j] += epsilon
            minus[i, j] -= epsilon
            numerical[i, j] = (
                two_pin_net_moving_objective(plus, target)
                - two_pin_net_moving_objective(minus, target)
            ) / (2.0 * epsilon)
    return numerical
