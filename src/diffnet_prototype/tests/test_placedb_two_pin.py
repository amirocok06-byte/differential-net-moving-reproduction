import torch

from dreamplace.placedb_two_pin import two_pin_pairs_from_flat_map


def main():
    flat = torch.tensor([10, 11, 20, 21, 22, 30, 31])
    starts = torch.tensor([0, 2, 5, 7])
    pairs = two_pin_pairs_from_flat_map(flat, starts)
    assert torch.equal(pairs, torch.tensor([[10, 11], [30, 31]]))
    empty = two_pin_pairs_from_flat_map(torch.tensor([1, 2, 3]), torch.tensor([0, 3]))
    assert empty.shape == (0, 2)
    try:
        two_pin_pairs_from_flat_map(flat, torch.tensor([1, 2, 5, 7]))
    except ValueError:
        pass
    else:
        raise AssertionError("invalid start map must be rejected")
    print("PlaceDB two-pin extraction test: PASS")


if __name__ == "__main__":
    main()
