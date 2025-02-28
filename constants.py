# constants.py

from reportlab.lib.pagesizes import letter

# Page Size
PAGE_WIDTH, PAGE_HEIGHT = letter

# Margins
MARGIN_TOP = 50
MARGIN_BOTTOM = 50
MARGIN_LEFT = 50
MARGIN_RIGHT = 50

# Text Wrapping
MAX_TEXT_WIDTH = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT

# Spacing
LINE_HEIGHT = 12
SECTION_SPACING = 20
JOB_SPACING = 10

# Font Sizes
FONT_HEADER = 18
FONT_SECTION_TITLE = 14
FONT_JOB_TITLE = 12
FONT_BODY = 10

# Font Styles
FONT_BOLD = "Helvetica-Bold"
FONT_NORMAL = "Helvetica"
FONT_ITALIC = "Helvetica-Oblique"

# Constants for Layout
COLUMN_GAP = 30  # Space between columns

# Adjusted Column Widths (70-30 Split)
COLUMN_WIDTH_LEFT = 0.7 * (PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT - COLUMN_GAP)  # 70%
COLUMN_WIDTH_RIGHT = 0.3 * (PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT - COLUMN_GAP)  # 30%