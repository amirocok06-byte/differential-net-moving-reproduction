"""Batch endpoint gradients from the paper congestion snapshot definitions."""

from typing import Dict

import torch

from dreamplace.paper_congestion import (
    poisson_source,
    solve_poisson_neumann_jacobi,
    potential_gradient_neumann,
)
from dreamplace.segment_normal_endpoint_gradient import endpoint_gradients
from dreamplace.segment_virtual_cell import select_hotspot_cell, virtual_cell_from_hotspot


def endpoint_gradients_from_snapshot(
    pin_positions: torch.Tensor,
    pin_pairs: torch.Tensor,
    demand: torch.Tensor,
    capacity: torch.Tensor,
    lower_bound: torch.Tensor,
    grid_size: torch.Tensor,
    *,
    iterations: int = 200,
    attribution: float = 0.5,
    distance_scale: float = 1.0,
) -> Dict[str, torch.Tensor]:
    """Generate ``(M,2,2)`` endpoint gradients from a detached snapshot.

    Positions are physical ``(x,y)`` coordinates; map indices are ``(x,y)``
    and are converted by the existing hotspot geometry probe.  The returned
    tensors are detached because demand/capacity and hotspot selection are a
    fixed router snapshot, not part of DREAMPlace autograd.
    """
    if pin_positions.ndim != 2 or pin_positions.shape[1] != 2:
        raise ValueError("pin_positions must have shape (num_pins, 2)")
    if pin_pairs.ndim != 2 or pin_pairs.shape[1] != 2:
        raise ValueError("pin_pairs must have shape (num_nets, 2)")
    if pin_pairs.numel() and (pin_pairs.min() < 0 or pin_pairs.max() >= pin_positions.shape[0]):
        raise ValueError("pin_pairs contain an invalid pin id")
    source = poisson_source(demand, capacity)
    phi = solve_poisson_neumann_jacobi(source, grid_size, iterations)
    gx, gy = potential_gradient_neumann(phi, grid_size)
    grads, hotspots, virtual_cells = [], [], []
    for pair in pin_pairs.long():
        start, end = pin_positions[pair[0]], pin_positions[pair[1]]
        index, hotspot = select_hotspot_cell(demand / capacity, start, end, lower_bound, grid_size)
        virtual = virtual_cell_from_hotspot(hotspot, start, end)
        raw = torch.stack((gx[index[1], index[0]], gy[index[1], index[0]]))
        _, g0, g1 = endpoint_gradients(raw, start, end, attribution, distance_scale)
        grads.append(torch.stack((g0, g1)))
        hotspots.append(hotspot)
        virtual_cells.append(virtual)
    shape = (0, 2, 2)
    return {
        "endpoint_gradients": torch.stack(grads) if grads else pin_positions.new_empty(shape),
        "hotspots": torch.stack(hotspots) if hotspots else pin_positions.new_empty((0, 2)),
        "virtual_cells": torch.stack(virtual_cells) if virtual_cells else pin_positions.new_empty((0, 2)),
        "poisson": phi.detach(),
        "potential_gradient": torch.stack((gx, gy)).detach(),
    }
