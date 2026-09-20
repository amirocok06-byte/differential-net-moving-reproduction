"""Detached audit trace for selected multi-pin cell moving."""

from typing import Dict

import torch


def build_selected_multi_pin_trace(
    *,
    pin_count: torch.Tensor,
    cell_congestion: torch.Tensor,
    baseline_gradient: torch.Tensor,
    congestion_gradient: torch.Tensor,
    selected_mask: torch.Tensor,
    selected_gradient: torch.Tensor,
    weight: float = 1.0,
    provenance: str = "synthetic-selected-multi-pin-cell",
) -> Dict[str, object]:
    """Return a detached CPU trace of the cell-moving gradient replacement."""
    tensors = {
        "pin_count": pin_count,
        "cell_congestion": cell_congestion,
        "baseline_gradient": baseline_gradient,
        "congestion_gradient": congestion_gradient,
        "selected_mask": selected_mask,
        "selected_gradient": selected_gradient,
    }
    if selected_mask.ndim != 1 or selected_gradient.shape != baseline_gradient.shape:
        raise ValueError("selected mask/gradient shapes are inconsistent")
    if baseline_gradient.ndim != 2 or baseline_gradient.shape[0] != selected_mask.numel():
        raise ValueError("gradient and selected mask sizes are inconsistent")
    return {
        "trace_kind": "selected-multi-pin-cell-moving",
        "provenance": provenance,
        "per_net_attribution_available": False,
        "weight": float(weight),
        **{name: value.detach().cpu().clone() for name, value in tensors.items()},
    }
