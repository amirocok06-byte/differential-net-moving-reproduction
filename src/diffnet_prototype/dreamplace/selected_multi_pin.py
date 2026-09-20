"""Independent selected multi-pin *cell* moving probe from Algorithm 2."""

from typing import Tuple

import torch


def selected_multi_pin_mask(
    pin_count: torch.Tensor,
    cell_congestion: torch.Tensor,
    threshold: float = 0.7,
) -> torch.Tensor:
    """Select cells with ``n_i > average_pin_count`` and ``C_i > threshold``."""
    if pin_count.ndim != 1 or cell_congestion.shape != pin_count.shape:
        raise ValueError("pin_count and cell_congestion must be matching 1-D tensors")
    if not torch.is_floating_point(cell_congestion):
        raise TypeError("cell_congestion must be floating point")
    if threshold < 0:
        raise ValueError("threshold must be non-negative")
    average = pin_count.to(dtype=cell_congestion.dtype).mean()
    return (pin_count > average) & (cell_congestion > threshold)


def apply_selected_multi_pin_gradient(
    baseline_gradient: torch.Tensor,
    congestion_gradient: torch.Tensor,
    pin_count: torch.Tensor,
    cell_congestion: torch.Tensor,
    threshold: float = 0.7,
) -> Tuple[torch.Tensor, torch.Tensor]:
    """Replace selected cell gradients with their congestion gradients.

    Returns ``(new_gradient, selected_mask)``.  This is explicitly cell
    moving, not a complete multi-pin net-moving implementation.
    """
    if baseline_gradient.shape != congestion_gradient.shape or baseline_gradient.ndim != 2:
        raise ValueError("gradient tensors must have matching shape (num_cells, dim)")
    if baseline_gradient.shape[0] != pin_count.numel():
        raise ValueError("gradient and cell metadata sizes must match")
    mask = selected_multi_pin_mask(pin_count, cell_congestion, threshold)
    return torch.where(mask.unsqueeze(-1), congestion_gradient, baseline_gradient), mask
