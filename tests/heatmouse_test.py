import pytest

from heatmouse import heatmouse_main


@pytest.fixture
def heat_mouse():
    """Fixture to create a HeatMouse instance."""
    return heatmouse_main.HeatMouse()


def test_heat_mouse(heat_mouse):
    """Test the initial temperature of the HeatMouse."""
    assert heat_mouse.window is None, "Initial window should be None."
