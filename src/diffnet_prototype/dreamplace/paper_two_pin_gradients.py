"""Batch two-pin endpoint gradients from a fixed paper congestion snapshot."""

from typing import Tuple

import torch

from dreamplace.paper_congestion import (
    poisson_source,
    potential_gradient_neumann,
    solve_poisson_neumann_jacobi,
)
from dreamplace.segment_normal_endpoint_gradient import endpoint_gradients
from dreamplace.paper_congestion import congestion_map


def _sample_segment_cells(
    start: torch.Tensor,
    end: torch.Tensor,
    lower_bound: torch.Tensor,
    grid_size: torch.Tensor,
    shape: Tuple[int, int],
    samples: int,
) -> torch.Tensor:
    points = torch.lerp(start, end, torch.linspace(
        0, 1, samples, dtype=start.dtype, device=start.device
    ).unsqueeze(1))
    xy = torch.floor((points - lower_bound) / grid_size).long()
    xy[:, 0].clamp_(0, shape[1] - 1)
    xy[:, 1].clamp_(0, shape[0] - 1)
    return xy


def batch_two_pin_endpoint_gradients(
    congestion: torch.Tensor,
    pin_positions: torch.Tensor,
    pin_pairs: torch.Tensor,
    lower_bound: torch.Tensor,
    grid_size: torch.Tensor,
    *,
    poisson_iterations: int = 200,
    samples_per_segment: int = 32,
    distance_scale: float = 1.0,
) -> Tuple[torch.Tensor, torch.Tensor]:
    """Return `(endpoint_gradients, hotspot_indices)` for two-pin pairs.

    `pin_positions` is `(2,P)` in `(x,y)` physical coordinates and
    `pin_pairs` is `(M,2)`.  The congestion map is `(H,W)` indexed `(y,x)`.
    The hotspot rule is explicitly segment-local sampling; it is replaceable
    if the paper's router implementation uses a different traversal rule.
    """
    if congestion.ndim != 2 or pin_positions.ndim != 2 or pin_positions.shape[0] != 2:
        raise ValueError("congestion must be (H,W), pin_positions must be (2,P)")
    if pin_pairs.ndim != 2 or pin_pairs.shape[1] != 2:
        raise ValueError("pin_pairs must be (M,2)")
    if lower_bound.shape != (2,) or grid_size.shape != (2,) or torch.any(grid_size <= 0):
        raise ValueError("bounds and grid_size must be positive shape (2,)")
    if samples_per_segment < 2:
        raise ValueError("samples_per_segment must be >= 2")
    source = poisson_source(congestion, congestion.new_ones(congestion.shape))
    phi = solve_poisson_neumann_jacobi(source, grid_size, poisson_iterations)
    gx, gy = potential_gradient_neumann(phi, grid_size)
    result = []
    hotspots = []
    for pair in pin_pairs:
        start = pin_positions[:, pair[0]]
        end = pin_positions[:, pair[1]]
        cells = _sample_segment_cells(start, end, lower_bound, grid_size, tuple(congestion.shape), samples_per_segment)
        values = congestion[cells[:, 1], cells[:, 0]]
        selected = cells[torch.argmax(values)]
        raw = torch.stack((gx[selected[1], selected[0]], gy[selected[1], selected[0]]))
        hotspot = lower_bound + (selected.to(grid_size.dtype) + 0.5) * grid_size
        virtual = start + torch.clamp(torch.dot(hotspot - start, end - start) / torch.dot(end - start, end - start), 0, 1) * (end - start) if torch.dot(end - start, end - start).item() else start
        attribution = torch.linalg.vector_norm(virtual - start) / torch.linalg.vector_norm(end - start) if torch.linalg.vector_norm(end - start).item() else torch.zeros((), dtype=start.dtype, device=start.device)
        _, start_gradient, end_gradient = endpoint_gradients(raw, start, end, attribution, distance_scale)
        result.append(torch.stack((start_gradient, end_gradient)))
        hotspots.append(selected)
    if not result:
        return congestion.new_empty((0, 2, 2)), torch.empty((0, 2), dtype=torch.long, device=congestion.device)
    return torch.stack(result), torch.stack(hotspots)


def batch_two_pin_paper_formula_proxy(
    demand: torch.Tensor,
    capacity: torch.Tensor,
    pin_positions: torch.Tensor,
    pin_pairs: torch.Tensor,
    lower_bound: torch.Tensor,
    grid_size: torch.Tensor,
    *,
    poisson_iterations: int = 200,
    return_trace: bool = False,
) -> Tuple[torch.Tensor, torch.Tensor]:
    """Paper Eq. (3),(6)--(9) using one global demand/capacity map.

    This is deliberately a *global-map proxy*: the same congestion field is
    sampled for every net because Xplace does not expose the author's
    per-net demand attribution.  It nevertheless follows the paper's
    candidate count, acute normal orientation, and ``L/(2*div)`` endpoint
    scaling exactly.
    """
    if demand.ndim != 2 or demand.shape != capacity.shape:
        raise ValueError("demand and capacity must be matching 2-D tensors")
    if pin_positions.ndim != 2 or pin_positions.shape[0] != 2:
        raise ValueError("pin_positions must be (2,P)")
    if pin_pairs.ndim != 2 or pin_pairs.shape[1] != 2:
        raise ValueError("pin_pairs must be (M,2)")
    congestion = congestion_map(demand, capacity)
    source = poisson_source(demand, capacity)
    phi = solve_poisson_neumann_jacobi(source, grid_size, poisson_iterations)
    gx, gy = potential_gradient_neumann(phi, grid_size)
    h, w = congestion.shape
    outputs, hotspots = [], []
    trace = {name: [] for name in (
        "segment_start", "segment_end", "virtual_cell", "raw_gradient",
        "normal", "projected_gradient", "segment_length", "div_start", "div_end",
    )}
    eps = torch.finfo(pin_positions.dtype).eps
    for pair in pin_pairs:
        p1, p2 = pin_positions[:, pair[0]], pin_positions[:, pair[1]]
        delta = p2 - p1
        length = torch.linalg.vector_norm(delta)
        if length.item() == 0:
            outputs.append(torch.zeros((2, 2), dtype=pin_positions.dtype, device=pin_positions.device))
            hotspots.append(torch.zeros(2, dtype=torch.long, device=pin_positions.device))
            trace["segment_start"].append(p1)
            trace["segment_end"].append(p2)
            trace["virtual_cell"].append(p1)
            trace["raw_gradient"].append(torch.zeros(2, dtype=pin_positions.dtype, device=pin_positions.device))
            trace["normal"].append(torch.zeros(2, dtype=pin_positions.dtype, device=pin_positions.device))
            trace["projected_gradient"].append(torch.zeros(2, dtype=pin_positions.dtype, device=pin_positions.device))
            trace["segment_length"].append(length)
            trace["div_start"].append(length.new_zeros(()))
            trace["div_end"].append(length.new_zeros(()))
            continue
        k = max(int(torch.floor(torch.abs(delta[0]) / grid_size[0]).item()),
                int(torch.floor(torch.abs(delta[1]) / grid_size[1]).item()))
        ts = torch.arange(1, k + 1, dtype=pin_positions.dtype, device=pin_positions.device) / (k + 1) if k else pin_positions.new_empty((0,))
        points = p1.unsqueeze(0) + ts.unsqueeze(1) * delta if k else p1.unsqueeze(0)
        cells = torch.floor((points - lower_bound) / grid_size).long()
        cells[:, 0].clamp_(0, w - 1); cells[:, 1].clamp_(0, h - 1)
        vals = congestion[cells[:, 1], cells[:, 0]]
        selected = cells[torch.argmax(vals)]
        virtual = lower_bound + (selected.to(grid_size.dtype) + 0.5) * grid_size
        raw = torch.stack((gx[selected[1], selected[0]], gy[selected[1], selected[0]]))
        tangent = delta / length
        normal = torch.stack((-tangent[1], tangent[0]))
        if torch.dot(normal, raw).item() < 0: normal = -normal
        projected = torch.dot(raw, normal) * normal
        div1 = torch.linalg.vector_norm(virtual - p1).clamp_min(eps)
        div2 = torch.linalg.vector_norm(virtual - p2).clamp_min(eps)
        outputs.append(torch.stack((length / (2 * div1) * projected,
                                    length / (2 * div2) * projected)))
        hotspots.append(selected)
        trace["segment_start"].append(p1)
        trace["segment_end"].append(p2)
        trace["virtual_cell"].append(virtual)
        trace["raw_gradient"].append(raw)
        trace["normal"].append(normal)
        trace["projected_gradient"].append(projected)
        trace["segment_length"].append(length)
        trace["div_start"].append(div1)
        trace["div_end"].append(div2)
    if not outputs:
        result = (pin_positions.new_empty((0, 2, 2)), torch.empty((0, 2), dtype=torch.long, device=pin_positions.device))
        if return_trace:
            return result[0], result[1], {name: pin_positions.new_empty((0, 2)) for name in trace if name not in ("segment_length", "div_start", "div_end")}
        return result
    result = (torch.stack(outputs), torch.stack(hotspots))
    if return_trace:
        trace_tensors = {name: torch.stack(values) for name, values in trace.items()}
        return result[0], result[1], trace_tensors
    return result
