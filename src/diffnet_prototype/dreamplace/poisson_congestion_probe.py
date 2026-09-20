"""Independent, assumption-marked discrete Poisson congestion probe.

This is not the paper implementation: it uses a zero-Dirichlet Jacobi solve
for ``L(phi) = congestion - mean(congestion)`` and finite differences for the
potential gradient.  It is intentionally isolated from the placer.
"""

from typing import Tuple

import torch


def solve_poisson_jacobi(source: torch.Tensor, iterations: int = 200) -> torch.Tensor:
    """Solve a 2-D five-point Poisson system with zero boundary potential."""
    if source.ndim != 2 or min(source.shape) < 3:
        raise ValueError("source must have shape (height, width), each >= 3")
    if iterations <= 0:
        raise ValueError("iterations must be positive")
    phi = torch.zeros_like(source)
    rhs = source - source.mean()
    for _ in range(iterations):
        updated = phi.clone()
        updated[1:-1, 1:-1] = 0.25 * (
            phi[:-2, 1:-1] + phi[2:, 1:-1] + phi[1:-1, :-2] + phi[1:-1, 2:] - rhs[1:-1, 1:-1]
        )
        phi = updated
    return phi


def potential_gradient(phi: torch.Tensor, grid_size: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
    """Return physical x/y potential derivatives from a grid potential."""
    if phi.ndim != 2 or grid_size.shape != (2,) or torch.any(grid_size <= 0):
        raise ValueError("phi must be 2-D and grid_size must be positive shape (2,)")
    gy = torch.zeros_like(phi)
    gx = torch.zeros_like(phi)
    gx[:, 1:-1] = (phi[:, 2:] - phi[:, :-2]) / (2 * grid_size[0])
    gy[1:-1, :] = (phi[2:, :] - phi[:-2, :]) / (2 * grid_size[1])
    gx[:, 0] = (phi[:, 1] - phi[:, 0]) / grid_size[0]
    gx[:, -1] = (phi[:, -1] - phi[:, -2]) / grid_size[0]
    gy[0, :] = (phi[1, :] - phi[0, :]) / grid_size[1]
    gy[-1, :] = (phi[-1, :] - phi[-2, :]) / grid_size[1]
    return gx, gy
