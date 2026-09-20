"""Explicitly labelled global-map attribution proxy.

This is not the paper's net-specific attribution: a global congestion map is
sampled along each segment because per-net demand data is unavailable.
"""

from typing import Dict

import torch

from dreamplace.paper_two_pin_gradients import batch_two_pin_endpoint_gradients


SOURCE = "global-map-attribution-proxy"


def endpoint_gradients_from_global_map(
    congestion: torch.Tensor,
    pin_positions: torch.Tensor,
    pin_pairs: torch.Tensor,
    lower_bound: torch.Tensor,
    grid_size: torch.Tensor,
    **options,
) -> Dict[str, object]:
    """Return endpoint gradients plus provenance metadata.

    The metadata is intentionally plain Python so it can be serialized with a
    debug trace and cannot be mistaken for an autograd tensor.
    """
    gradients, hotspots = batch_two_pin_endpoint_gradients(
        congestion, pin_positions, pin_pairs, lower_bound, grid_size, **options
    )
    return {
        "endpoint_gradients": gradients.detach(),
        "hotspot_indices": hotspots.detach(),
        "attribution_source": SOURCE,
        "per_net_demand_available": False,
        "assumptions": (
            "segment-local hotspot sampling",
            "global demand/capacity map used as proxy",
            "paper endpoint formula not independently verified",
        ),
    }
