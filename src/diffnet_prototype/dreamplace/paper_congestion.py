"""Independent implementation of the congestion definitions stated in the paper.

This module is intentionally separate from the existing assumption-marked
Dirichlet probe.  The paper uses the demand/capacity ratio as the Poisson
source and a zero-normal-gradient boundary condition.
"""

from typing import Tuple

import torch


def congestion_map(demand: torch.Tensor, capacity: torch.Tensor) -> torch.Tensor:
    """Return ``max(demand / capacity - 1, 0)`` elementwise."""
    if demand.shape != capacity.shape or demand.ndim != 2:
        raise ValueError("demand and capacity must be matching 2-D tensors")
    if not torch.is_floating_point(demand) or not torch.is_floating_point(capacity):
        raise TypeError("demand and capacity must be floating-point tensors")
    if torch.any(capacity <= 0):
        raise ValueError("capacity must be positive")
    return torch.relu(demand / capacity - 1)


def poisson_source(demand: torch.Tensor, capacity: torch.Tensor) -> torch.Tensor:
    """Return the centered ``Dmd/Cap`` source required by Neumann compatibility."""
    ratio = demand / capacity
    return ratio - ratio.mean()


def solve_poisson_neumann_jacobi(
    source: torch.Tensor, grid_size: torch.Tensor, iterations: int = 200
) -> torch.Tensor:
    """Solve ``laplacian(phi) = -source`` with zero normal flux boundaries.

    The constant-potential nullspace is fixed by subtracting the mean after
    each Jacobi iteration.  ``grid_size`` is ``(dx, dy)`` in physical units.
    """
    if source.ndim != 2 or min(source.shape) < 2:
        raise ValueError("source must be 2-D with both dimensions >= 2")
    if grid_size.shape != (2,) or torch.any(grid_size <= 0):
        raise ValueError("grid_size must be positive with shape (2,)")
    if iterations <= 0:
        raise ValueError("iterations must be positive")
    dx, dy = grid_size[0], grid_size[1]
    phi = torch.zeros_like(source)
    rhs = source - source.mean()
    ax, ay = 1 / (dx * dx), 1 / (dy * dy)
    denom = 2 * (ax + ay)
    for _ in range(iterations):
        padded = torch.nn.functional.pad(phi.unsqueeze(0).unsqueeze(0), (1, 1, 1, 1), mode="replicate")[0, 0]
        east_west = (padded[1:-1, :-2] + padded[1:-1, 2:]) * ax
        north_south = (padded[:-2, 1:-1] + padded[2:, 1:-1]) * ay
        phi = (east_west + north_south + rhs) / denom
        phi = phi - phi.mean()
    return phi


def potential_gradient_neumann(
    phi: torch.Tensor, grid_size: torch.Tensor
) -> Tuple[torch.Tensor, torch.Tensor]:
    """Return physical potential gradients with zero normal boundary values."""
    if phi.ndim != 2 or min(phi.shape) < 2 or grid_size.shape != (2,):
        raise ValueError("phi must be 2-D and grid_size must have shape (2,)")
    if torch.any(grid_size <= 0):
        raise ValueError("grid_size must be positive")
    gx = torch.zeros_like(phi)
    gy = torch.zeros_like(phi)
    gx[:, 1:-1] = (phi[:, 2:] - phi[:, :-2]) / (2 * grid_size[0])
    gy[1:-1, :] = (phi[2:, :] - phi[:-2, :]) / (2 * grid_size[1])
    return gx, gy


def lambda2_from_gradients(
    wirelength_gradient: torch.Tensor,
    congestion_gradient: torch.Tensor,
    congestion_cells: int,
    num_cells: int,
) -> torch.Tensor:
    """Implement paper Eq. (10)'s ``2*N_C/N * ||grad W||_1/||grad C||_1``."""
    if wirelength_gradient.shape != congestion_gradient.shape:
        raise ValueError("gradient tensors must have matching shapes")
    if congestion_cells < 0 or num_cells <= 0:
        raise ValueError("invalid cell counts")
    denominator = congestion_gradient.abs().sum()
    if denominator.item() == 0:
        return torch.zeros((), dtype=wirelength_gradient.dtype, device=wirelength_gradient.device)
    return (2.0 * congestion_cells / num_cells) * wirelength_gradient.abs().sum() / denominator
