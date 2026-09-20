"""Independent geometry probe for segment, hotspot, and virtual-cell mapping."""

from typing import Optional, Tuple

import torch


def segment_projection(point: torch.Tensor, start: torch.Tensor, end: torch.Tensor) -> torch.Tensor:
    """Project a continuous point onto a two-dimensional segment."""
    if point.shape != (2,) or start.shape != (2,) or end.shape != (2,):
        raise ValueError("point, start, and end must have shape (2,)")
    direction = end - start
    denominator = torch.dot(direction, direction)
    if denominator.item() == 0:
        return start.clone()
    ratio = torch.dot(point - start, direction) / denominator
    ratio = torch.clamp(ratio, 0.0, 1.0)
    return start + ratio * direction


def grid_cell_center(
    index: torch.Tensor,
    lower_bound: torch.Tensor,
    grid_size: torch.Tensor,
) -> torch.Tensor:
    """Convert an integer ``(x, y)`` grid index to its physical center."""
    if index.shape != (2,) or lower_bound.shape != (2,) or grid_size.shape != (2,):
        raise ValueError("index, lower_bound, and grid_size must have shape (2,)")
    if not torch.all(grid_size > 0):
        raise ValueError("grid_size must be positive")
    return lower_bound + (index.to(lower_bound.dtype) + 0.5) * grid_size


def select_hotspot_cell(
    congestion: torch.Tensor,
    segment_start: torch.Tensor,
    segment_end: torch.Tensor,
    lower_bound: torch.Tensor,
    grid_size: torch.Tensor,
) -> Tuple[torch.Tensor, torch.Tensor]:
    """Select the highest-congestion cell and return index and physical center.

    This is a deterministic synthetic rule: the global maximum is selected.
    Neighborhood filtering and the paper's exact hotspot rule remain future
    work until the original formula is available.
    """
    del segment_start, segment_end  # reserved for a future segment-local mask
    if congestion.ndim != 2:
        raise ValueError("congestion must have shape (num_y, num_x)")
    flat_index = torch.argmax(congestion)
    row = torch.div(flat_index, congestion.shape[1], rounding_mode="floor")
    col = flat_index.remainder(congestion.shape[1])
    index = torch.stack((col, row)).to(torch.int64)
    return index, grid_cell_center(index, lower_bound, grid_size)


def virtual_cell_from_hotspot(
    hotspot: torch.Tensor,
    segment_start: torch.Tensor,
    segment_end: torch.Tensor,
) -> torch.Tensor:
    """Project a hotspot center onto the two-pin segment."""
    return segment_projection(hotspot, segment_start, segment_end)
