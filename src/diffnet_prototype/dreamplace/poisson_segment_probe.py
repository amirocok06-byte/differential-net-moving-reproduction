"""Independent composition of the congestion-to-endpoint probe chain.

This module intentionally does not modify PlaceObj or NonLinearPlace.  The
discrete Poisson solve and hotspot rule are explicit reconstruction
assumptions; callers can inspect every intermediate result.
"""

from typing import Dict, Union

import torch

from dreamplace.poisson_congestion_probe import potential_gradient, solve_poisson_jacobi
from dreamplace.segment_normal_endpoint_gradient import endpoint_gradients
from dreamplace.segment_virtual_cell import select_hotspot_cell, virtual_cell_from_hotspot


def congestion_segment_endpoint_probe(
    congestion: torch.Tensor,
    segment_start: torch.Tensor,
    segment_end: torch.Tensor,
    lower_bound: torch.Tensor,
    grid_size: torch.Tensor,
    *,
    iterations: int = 200,
    attribution: Union[torch.Tensor, float] = 0.5,
    distance_scale: Union[torch.Tensor, float] = 1.0,
) -> Dict[str, torch.Tensor]:
    """Run hotspot -> virtual cell -> potential gradient -> endpoint chain."""
    phi = solve_poisson_jacobi(congestion, iterations)
    gx, gy = potential_gradient(phi, grid_size)
    index, hotspot = select_hotspot_cell(congestion, segment_start, segment_end, lower_bound, grid_size)
    virtual_cell = virtual_cell_from_hotspot(hotspot, segment_start, segment_end)
    # The current discrete assumption attributes the selected cell gradient.
    raw = torch.stack((gx[index[1], index[0]], gy[index[1], index[0]]))
    projected, start_gradient, end_gradient = endpoint_gradients(
        raw, segment_start, segment_end, attribution, distance_scale
    )
    return {
        "poisson": phi,
        "hotspot_index": index,
        "hotspot": hotspot,
        "virtual_cell": virtual_cell,
        "raw_gradient": raw,
        "projected_gradient": projected,
        "start_gradient": start_gradient,
        "end_gradient": end_gradient,
    }
