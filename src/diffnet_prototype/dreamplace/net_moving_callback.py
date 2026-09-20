"""Differentiable, opt-in bridge from precomputed net gradients to placement.

The router/congestion map is intentionally supplied by the caller.  This
keeps routing estimation outside the objective while making the final
endpoint gradient differentiable through DREAMPlace's ``pin_pos_op``.
"""

from typing import Callable

import torch

from dreamplace.placedb_two_pin import two_pin_pairs_from_flat_map
from dreamplace.paper_two_pin_gradients import batch_two_pin_endpoint_gradients


def make_two_pin_objective(
    pin_pos_op: Callable[[torch.Tensor], torch.Tensor],
    pin_pairs: torch.Tensor,
    endpoint_gradients: torch.Tensor,
    *,
    weight: float = 1.0,
) -> Callable[[torch.Tensor], torch.Tensor]:
    """Build a scalar linear objective with prescribed two-pin gradients.

    ``pin_pairs`` has shape ``(M,2)`` and indexes pin ids.  The pin-position
    tensor returned by DREAMPlace is flattened as ``[x_all_pins, y_all_pins]``
    (shape ``(2P,)``) or shaped ``(2,P)``.  ``endpoint_gradients`` has shape
    ``(M,2,2)``: net, endpoint, `(gx, gy)`.  The supplied gradients are
    detached because they come from a fixed router snapshot; differentiability
    is retained from pin positions back to cell positions.
    """
    if pin_pairs.ndim != 2 or pin_pairs.shape[1] != 2:
        raise ValueError("pin_pairs must have shape (num_nets, 2)")
    if endpoint_gradients.shape != (pin_pairs.shape[0], 2, 2):
        raise ValueError("endpoint_gradients must have shape (num_nets, 2, 2)")
    if not torch.is_floating_point(endpoint_gradients):
        raise TypeError("endpoint_gradients must be floating point")
    pairs = pin_pairs.to(dtype=torch.long)
    gradients = endpoint_gradients.detach()
    scalar_weight = float(weight)

    def objective(pos: torch.Tensor) -> torch.Tensor:
        pin_pos = pin_pos_op(pos)
        if pin_pos.ndim == 1:
            if pin_pos.numel() % 2:
                raise ValueError("flattened pin positions must have even length")
            pin_pos = pin_pos.view(2, -1)
        if pin_pos.ndim != 2 or pin_pos.shape[0] != 2:
            raise ValueError("pin_pos_op must return shape (2, num_pins) or (2*num_pins,)")
        p0, p1 = pairs[:, 0], pairs[:, 1]
        x = pin_pos[0]
        y = pin_pos[1]
        values = (
            x[p0] * gradients[:, 0, 0].to(x) + y[p0] * gradients[:, 0, 1].to(y)
            + x[p1] * gradients[:, 1, 0].to(x) + y[p1] * gradients[:, 1, 1].to(y)
        )
        return scalar_weight * values.sum()

    return objective


def make_two_pin_objective_from_flat_map(
    pin_pos_op: Callable[[torch.Tensor], torch.Tensor],
    flat_net2pin_map: torch.Tensor,
    flat_net2pin_start_map: torch.Tensor,
    endpoint_gradients: torch.Tensor,
    *,
    weight: float = 1.0,
) -> Callable[[torch.Tensor], torch.Tensor]:
    """Construct the callback directly from PlaceDB flat net-pin arrays."""
    pairs = two_pin_pairs_from_flat_map(flat_net2pin_map, flat_net2pin_start_map)
    if endpoint_gradients.shape[0] != pairs.shape[0]:
        raise ValueError("endpoint_gradients count must match extracted two-pin nets")
    return make_two_pin_objective(pin_pos_op, pairs, endpoint_gradients, weight=weight)


def make_two_pin_objective_from_congestion_snapshot(
    pin_pos_op: Callable[[torch.Tensor], torch.Tensor],
    pin_positions: torch.Tensor,
    flat_net2pin_map: torch.Tensor,
    flat_net2pin_start_map: torch.Tensor,
    congestion: torch.Tensor,
    lower_bound: torch.Tensor,
    grid_size: torch.Tensor,
    *,
    weight: float = 1.0,
    **gradient_options,
) -> tuple[Callable[[torch.Tensor], torch.Tensor], torch.Tensor, torch.Tensor]:
    """Build an opt-in placement callback from a fixed congestion snapshot.

    Returns ``(objective, endpoint_gradients, hotspot_indices)`` so callers can
    persist an audit trace.  The snapshot-to-gradient stage is detached; only
    the callback's pin-position-to-placement path is autograd-enabled.
    """
    pairs = two_pin_pairs_from_flat_map(flat_net2pin_map, flat_net2pin_start_map)
    endpoint_gradients, hotspots = batch_two_pin_endpoint_gradients(
        congestion, pin_positions, pairs, lower_bound, grid_size, **gradient_options
    )
    objective = make_two_pin_objective(pin_pos_op, pairs, endpoint_gradients, weight=weight)
    return objective, endpoint_gradients, hotspots
