"""Independent probe for segment-normal and endpoint gradient attribution."""

from typing import Tuple, Union

import torch


def segment_tangent_normal(start: torch.Tensor, end: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
    """Return unit tangent and counter-clockwise unit normal for a segment."""
    if start.shape != (2,) or end.shape != (2,):
        raise ValueError("start and end must have shape (2,)")
    direction = end - start
    length = torch.linalg.vector_norm(direction)
    if length.item() == 0:
        raise ValueError("a normal is undefined for a degenerate segment")
    tangent = direction / length
    normal = torch.stack((-tangent[1], tangent[0]))
    return tangent, normal


def project_gradient_to_normal(raw_gradient: torch.Tensor, normal: torch.Tensor) -> torch.Tensor:
    """Keep only the component of a raw gradient along a unit normal."""
    if raw_gradient.shape != (2,) or normal.shape != (2,):
        raise ValueError("raw_gradient and normal must have shape (2,)")
    return torch.dot(raw_gradient, normal) * normal


def endpoint_gradients(
    raw_gradient: torch.Tensor,
    start: torch.Tensor,
    end: torch.Tensor,
    attribution: Union[torch.Tensor, float] = 0.5,
    distance_scale: Union[torch.Tensor, float] = 1.0,
) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Project a gradient to the segment normal and attribute it to endpoints.

    ``attribution`` is the virtual-cell interpolation fraction from start to end.
    Thus a virtual-cell gradient ``g`` maps to ``(1-a)g`` and ``a*g``.
    The sign convention is intentionally explicit and can be replaced once the
    paper's endpoint convention is confirmed.
    """
    _, normal = segment_tangent_normal(start, end)
    projected = project_gradient_to_normal(raw_gradient, normal) * distance_scale
    a = torch.as_tensor(attribution, dtype=projected.dtype, device=projected.device)
    if a.numel() != 1 or a.item() < 0 or a.item() > 1:
        raise ValueError("attribution must be a scalar in [0, 1]")
    return projected, (1 - a) * projected, a * projected
