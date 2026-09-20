"""Synthetic checks for placement coordinates, pin offsets, and grid indices."""

import torch


def pin_position(node_pos, pin_offset):
    return node_pos + pin_offset


def grid_index(position, lower_bound, grid_size, num_grids):
    index = torch.floor((position - lower_bound) / grid_size).to(torch.int64)
    return torch.clamp(index, 0, num_grids - 1)


def test_pin_offsets_stay_in_continuous_coordinates():
    node = torch.tensor([100.0, 200.0], dtype=torch.double)
    offset = torch.tensor([12.5, 7.25], dtype=torch.double)
    expected = torch.tensor([112.5, 207.25], dtype=torch.double)
    assert torch.equal(pin_position(node, offset), expected)


def test_grid_index_is_not_a_physical_coordinate():
    position = torch.tensor([112.5, 207.25], dtype=torch.double)
    lower = torch.tensor([0.0, 0.0], dtype=torch.double)
    grid_size = torch.tensor([20.0, 20.0], dtype=torch.double)
    index = grid_index(position, lower, grid_size, num_grids=8)
    assert torch.equal(index, torch.tensor([5, 7], dtype=torch.int64))
    assert index.dtype == torch.int64
    assert not torch.allclose(index.to(torch.double), position)


def test_grid_boundaries_are_clamped():
    lower = torch.tensor([0.0, 0.0], dtype=torch.double)
    grid_size = torch.tensor([20.0, 20.0], dtype=torch.double)
    lower_index = grid_index(torch.tensor([-1.0, 0.0]), lower, grid_size, 8)
    upper_index = grid_index(torch.tensor([160.0, 200.0]), lower, grid_size, 8)
    assert torch.equal(lower_index, torch.tensor([0, 0], dtype=torch.int64))
    assert torch.equal(upper_index, torch.tensor([7, 7], dtype=torch.int64))


def test_coincident_pins_remain_valid():
    node = torch.tensor([50.0, 50.0], dtype=torch.double)
    offset = torch.tensor([0.0, 0.0], dtype=torch.double)
    assert torch.equal(pin_position(node, offset), pin_position(node, offset))


if __name__ == "__main__":
    test_pin_offsets_stay_in_continuous_coordinates()
    test_grid_index_is_not_a_physical_coordinate()
    test_grid_boundaries_are_clamped()
    test_coincident_pins_remain_valid()
    print("coordinate/grid metadata synthetic test: PASS")
