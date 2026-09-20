import torch

from dreamplace.poisson_segment_probe import congestion_segment_endpoint_probe


def main():
    congestion = torch.tensor(
        [[0.0, 0.0, 0.0, 0.0], [0.0, 1.0, 2.0, 0.0], [0.0, 3.0, 5.0, 0.0], [0.0, 0.0, 0.0, 0.0]],
        dtype=torch.float64,
    )
    start = torch.tensor([0.5, 1.5], dtype=torch.float64)
    end = torch.tensor([3.5, 1.5], dtype=torch.float64)
    result = congestion_segment_endpoint_probe(
        congestion, start, end, torch.zeros(2, dtype=torch.float64), torch.ones(2, dtype=torch.float64),
        iterations=80, attribution=0.25, distance_scale=2.0,
    )
    assert result["hotspot_index"].tolist() == [2, 2]
    assert torch.allclose(result["virtual_cell"], torch.tensor([2.5, 1.5], dtype=torch.float64))
    assert torch.isfinite(result["poisson"]).all()
    assert torch.allclose(result["start_gradient"] + result["end_gradient"], result["projected_gradient"])
    assert torch.allclose(result["end_gradient"], result["projected_gradient"] * 0.25)
    assert torch.allclose(torch.dot(result["projected_gradient"], end - start), torch.tensor(0.0, dtype=torch.float64))
    print("Poisson/segment endpoint composition test: PASS")


if __name__ == "__main__":
    main()
