import torch

from dreamplace.selected_multi_pin_callback import make_selected_multi_pin_objective


def main():
    baseline = torch.ones(4, 2)
    congestion = torch.tensor([[2.0, 3.0], [4.0, 5.0], [6.0, 7.0], [8.0, 9.0]])
    pin_count = torch.tensor([1, 3, 2, 5])
    cell_congestion = torch.tensor([0.9, 0.8, 0.6, 0.95])
    objective, mask, selected = make_selected_multi_pin_objective(
        baseline, congestion, pin_count, cell_congestion)
    assert torch.equal(mask, torch.tensor([False, True, False, True]))
    pos = torch.arange(8, dtype=torch.float32, requires_grad=True)
    value = objective(pos)
    value.backward()
    assert torch.allclose(pos.grad.view(2, 4).t(), selected)
    with torch.no_grad():
        pos -= 1e-3 * pos.grad
    assert torch.isfinite(pos).all()
    print("selected multi-pin callback test: PASS")


if __name__ == "__main__":
    main()
