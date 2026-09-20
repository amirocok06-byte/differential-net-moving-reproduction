"""Opt-in placement callback for selected multi-pin cell gradients."""

import torch

from dreamplace.selected_multi_pin import apply_selected_multi_pin_gradient


def make_selected_multi_pin_objective(
    baseline_gradient: torch.Tensor,
    congestion_gradient: torch.Tensor,
    pin_count: torch.Tensor,
    cell_congestion: torch.Tensor,
    *,
    threshold: float = 0.7,
    weight: float = 1.0,
):
    """Return ``(objective, selected_mask, selected_gradient)``.

    The metadata and gradients are a detached snapshot; autograd is retained
    only from the placement tensor to the scalar linear objective.
    """
    selected_gradient, mask = apply_selected_multi_pin_gradient(
        baseline_gradient, congestion_gradient, pin_count, cell_congestion, threshold
    )
    selected_gradient = selected_gradient.detach()

    def objective(pos: torch.Tensor) -> torch.Tensor:
        shaped = pos.view(2, -1)
        if shaped.shape[1] != selected_gradient.shape[0]:
            raise ValueError("pos cell count does not match selected gradient")
        return float(weight) * (shaped.t() * selected_gradient.to(shaped)).sum()

    return objective, mask.detach(), selected_gradient
