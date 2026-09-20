"""Serializable debug trace for the independent net-moving probe chain.

The trace is deliberately separate from the placer.  It records the
intermediate geometry and gradients needed to audit Algorithm 1 without
claiming that the current reconstruction is the paper's exact formula.
"""

from typing import Dict, Mapping, Union

import torch


_REQUIRED = (
    "hotspot_index",
    "hotspot",
    "virtual_cell",
    "raw_gradient",
    "projected_gradient",
    "start_gradient",
    "end_gradient",
)


def build_net_moving_trace(
    probe: Mapping[str, torch.Tensor],
    *,
    net_id: int = -1,
    segment_start: torch.Tensor,
    segment_end: torch.Tensor,
    attribution: Union[torch.Tensor, float] = 0.5,
    distance_scale: Union[torch.Tensor, float] = 1.0,
) -> Dict[str, object]:
    """Return a detached, CPU-friendly trace with stable field names.

    The input is the dictionary returned by
    ``congestion_segment_endpoint_probe``.  Values are detached so saving a
    trace cannot retain an autograd graph; vector fields remain tensors and
    scalar metadata remains ordinary Python values.
    """
    missing = [name for name in _REQUIRED if name not in probe]
    if missing:
        raise KeyError("probe is missing trace fields: " + ", ".join(missing))
    if segment_start.shape != (2,) or segment_end.shape != (2,):
        raise ValueError("segment_start and segment_end must have shape (2,)")

    def detached(name: str) -> torch.Tensor:
        value = probe[name]
        if not isinstance(value, torch.Tensor):
            raise TypeError(f"probe[{name!r}] must be a tensor")
        return value.detach().cpu().clone()

    a = torch.as_tensor(attribution).detach().cpu().item()
    scale = torch.as_tensor(distance_scale).detach().cpu().item()
    return {
        "net_id": int(net_id),
        "segment_start": segment_start.detach().cpu().clone(),
        "segment_end": segment_end.detach().cpu().clone(),
        "attribution": float(a),
        "distance_scale": float(scale),
        **{name: detached(name) for name in _REQUIRED},
    }


def trace_row(trace: Mapping[str, object]) -> Dict[str, object]:
    """Flatten a trace into one CSV-compatible summary row."""
    row: Dict[str, object] = {
        "net_id": trace["net_id"],
        "attribution": trace["attribution"],
        "distance_scale": trace["distance_scale"],
    }
    for name in ("segment_start", "segment_end", "hotspot", "virtual_cell",
                 "raw_gradient", "projected_gradient", "start_gradient", "end_gradient"):
        value = trace[name]
        if not isinstance(value, torch.Tensor):
            raise TypeError(f"trace[{name!r}] must be a tensor")
        for axis, component in enumerate(value.reshape(-1).tolist()):
            row[f"{name}_{axis}"] = float(component)
    index = trace["hotspot_index"]
    if not isinstance(index, torch.Tensor) or index.numel() != 2:
        raise ValueError("hotspot_index must contain two values")
    row["hotspot_index_x"] = int(index.reshape(-1)[0].item())
    row["hotspot_index_y"] = int(index.reshape(-1)[1].item())
    return row
