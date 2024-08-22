"""Common plotting functions for ASPLOS paper."""

# Adding the freaking calibri font

FONT_PATH = "../common/calibri-regular.ttf"
CM = 1/2.54  # cm to inch
FORMATS = ['pdf', 'png', 'svg']


def load_font(font_path: str):
    """Load a custom font to be used in the plots."""
    from matplotlib import font_manager
    try:
        font_manager.fontManager.addfont(font_path)
    except FileNotFoundError:
        pass
