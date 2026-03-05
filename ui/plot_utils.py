import matplotlib.pyplot as plt

# Professional Aesthetic Constants
COLORS = {
    "bg": "#11111B",
    "panel": "#181825",
    "text": "#CDD6F4",
    "primary": "#F38BA8",
    "secondary": "#89DCEB",
    "accent": "#CBA6F7",
    "border": "#313244",
    "benchmark": "#F9E2AF"
}

def apply_modern_theme(ax, title=""):
    """Applies a consistent modern dark theme to a matplotlib axes."""
    ax.set_facecolor(COLORS["panel"])
    ax.tick_params(colors=COLORS["text"])
    for spine in ax.spines.values():
        spine.set_color(COLORS["border"])
    
    if title:
        ax.set_title(title, color=COLORS["accent"], weight='bold', pad=15)
        
    ax.grid(True, linestyle='--', alpha=0.2, color=COLORS["text"])

def apply_figure_theme(fig):
    """Applies a consistent modern dark theme to a matplotlib figure."""
    fig.patch.set_facecolor(COLORS["bg"])
