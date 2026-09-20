import torch

from dreamplace.selected_multi_pin import (
    apply_selected_multi_pin_gradient,
    selected_multi_pin_mask,
)


def main():
    pin_count = torch.tensor([1, 2, 4, 5])
    congestion = torch.tensor([0.9, 0.8, 0.71, 0.6])
    mask = selected_multi_pin_mask(pin_count, congestion)
    assert torch.equal(mask, torch.tensor([False, False, True, False]))
    base = torch.zeros(4, 2)
    congestion_gradient = torch.arange(8, dtype=torch.float32).reshape(4, 2)
    updated, selected = apply_selected_multi_pin_gradient(
        base, congestion_gradient, pin_count, congestion
    )
    assert torch.equal(selected, mask)
    assert torch.equal(updated[2], congestion_gradient[2])
    assert torch.equal(updated[0], base[0])
    print("selected multi-pin cell test: PASS")


if __name__ == "__main__":
    main()
