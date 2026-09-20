"""Synthetic tests for segment/hotspot/virtual-cell geometry."""

import torch

from dreamplace.segment_virtual_cell import (
    grid_cell_center,
    select_hotspot_cell,
    segment_projection,
    virtual_cell_from_hotspot,
)


def test_grid_cell_center_uses_physical_coordinates():
    index = torch.tensor([2, 1], dtype=torch.int64)
    lower = torch.tensor([0.0, 10.0], dtype=torch.double)
    size = torch.tensor([20.0, 4.0], dtype=torch.double)
    torch.testing.assert_close(
        grid_cell_center(index, lower, size),
        torch.tensor([50.0, 16.0], dtype=torch.double),
    )


def test_select_hotspot_cell_returns_xy_index_and_center():
    congestion = torch.tensor([[0.1, 0.2, 0.3], [0.4, 0.9, 0.5]], dtype=torch.double)
    start = torch.tensor([0.0, 0.0], dtype=torch.double)
    end = torch.tensor([100.0, 0.0], dtype=torch.double)
    lower = torch.tensor([0.0, 0.0], dtype=torch.double)
    size = torch.tensor([10.0, 20.0], dtype=torch.double)

    index, center = select_hotspot_cell(congestion, start, end, lower, size)

    assert torch.equal(index, torch.tensor([1, 1], dtype=torch.int64))
    torch.testing.assert_close(center, torch.tensor([15.0, 30.0], dtype=torch.double))


def test_virtual_cell_is_hotspot_projection_on_segment():
    start = torch.tensor([0.0, 0.0], dtype=torch.double)
    end = torch.tensor([10.0, 0.0], dtype=torch.double)
    hotspot = torch.tensor([7.0, 3.0], dtype=torch.double)

    virtual = virtual_cell_from_hotspot(hotspot, start, end)

    torch.testing.assert_close(virtual, torch.tensor([7.0, 0.0], dtype=torch.double))


def test_degenerate_segment_returns_start():
    point = torch.tensor([7.0, 3.0], dtype=torch.double)
    start = torch.tensor([2.0, 4.0], dtype=torch.double)
    torch.testing.assert_close(segment_projection(point, start, start), start)


if __name__ == "__main__":
    test_grid_cell_center_uses_physical_coordinates()
    test_select_hotspot_cell_returns_xy_index_and_center()
    test_virtual_cell_is_hotspot_projection_on_segment()
    test_degenerate_segment_returns_start()
    print("segment/hotspot/virtual-cell geometry test: PASS")
