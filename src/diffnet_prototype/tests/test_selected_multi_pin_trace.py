import torch

from dreamplace.selected_multi_pin import apply_selected_multi_pin_gradient
from dreamplace.selected_multi_pin_trace import build_selected_multi_pin_trace


def main():
    baseline = torch.ones(4, 2)
    congestion = torch.tensor([[2.0, 3.0], [4.0, 5.0], [6.0, 7.0], [8.0, 9.0]])
    pin_count = torch.tensor([1, 3, 2, 5])
    cell_congestion = torch.tensor([0.9, 0.8, 0.6, 0.95])
    selected, mask = apply_selected_multi_pin_gradient(
        baseline, congestion, pin_count, cell_congestion)
    trace = build_selected_multi_pin_trace(
        pin_count=pin_count, cell_congestion=cell_congestion,
        baseline_gradient=baseline, congestion_gradient=congestion,
        selected_mask=mask, selected_gradient=selected)
    assert torch.equal(trace["selected_mask"], torch.tensor([False, True, False, True]))
    assert trace["selected_gradient"].shape == (4, 2)
    assert trace["selected_gradient"].device.type == "cpu"
    assert trace["per_net_attribution_available"] is False
    assert torch.equal(trace["selected_gradient"][mask], congestion[mask])
    assert torch.equal(trace["selected_gradient"][~mask], baseline[~mask])
    print("selected multi-pin trace test: PASS")


if __name__ == "__main__":
    main()
