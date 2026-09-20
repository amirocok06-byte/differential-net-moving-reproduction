"""Extract two-pin net pin-id pairs from DREAMPlace PlaceDB arrays."""

import torch


def two_pin_pairs_from_flat_map(
    flat_net2pin_map: torch.Tensor,
    flat_net2pin_start_map: torch.Tensor,
    *,
    max_net_degree: int = 2,
) -> torch.Tensor:
    """Return `(M,2)` pin ids for exactly-two-pin nets.

    The start map has length `num_nets + 1`; no pin coordinates are copied or
    reordered.  `max_net_degree` is retained as explicit metadata but a value
    other than 2 is rejected because this interface is strictly two-pin.
    """
    if max_net_degree != 2:
        raise ValueError("two-pin extractor only accepts max_net_degree=2")
    if flat_net2pin_map.ndim != 1 or flat_net2pin_start_map.ndim != 1:
        raise ValueError("flat maps must be 1-D")
    if flat_net2pin_start_map.numel() == 0 or flat_net2pin_start_map[0].item() != 0:
        raise ValueError("start map must begin at zero")
    if flat_net2pin_start_map[-1].item() != flat_net2pin_map.numel():
        raise ValueError("start map terminator must equal flat map length")
    lengths = flat_net2pin_start_map[1:] - flat_net2pin_start_map[:-1]
    starts = flat_net2pin_start_map[:-1][lengths == 2]
    if starts.numel() == 0:
        return flat_net2pin_map.new_empty((0, 2), dtype=torch.long)
    return torch.stack((flat_net2pin_map[starts], flat_net2pin_map[starts + 1]), dim=1).long()
