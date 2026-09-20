import torch

from dreamplace.global_map_attribution_proxy import (
    SOURCE,
    endpoint_gradients_from_global_map,
)


def main():
    congestion = torch.zeros(4, 4)
    congestion[1, 2] = 3.0
    positions = torch.tensor([[0.5, 3.5], [0.5, 3.5]])
    result = endpoint_gradients_from_global_map(
        congestion, positions, torch.tensor([[0, 1]]),
        torch.zeros(2), torch.ones(2), poisson_iterations=8, samples_per_segment=8
    )
    assert result["endpoint_gradients"].shape == (1, 2, 2)
    assert result["hotspot_indices"].shape == (1, 2)
    assert result["attribution_source"] == SOURCE
    assert result["per_net_demand_available"] is False
    assert torch.isfinite(result["endpoint_gradients"]).all()
    print("global-map attribution proxy test: PASS")


if __name__ == "__main__":
    main()
