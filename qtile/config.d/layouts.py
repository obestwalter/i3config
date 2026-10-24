"""Layouts and floating layout rules.

Converted from:
- config.d/0-basic-setup.conf:
  - workspace_layout tabbed
  - new_window normal 1px
  - new_float normal 3px
  - hide_edge_borders smart
- config.d/3-window-settings.conf:
  - for_window [class="xfdesktop"] floating enable
"""

from __future__ import annotations

from typing import Any

from libqtile import layout
from libqtile.config import Match

from settings import FONT_FAMILY, get_active_theme, get_font_size


def build_layouts() -> list[Any]:
    """Build Qtile layouts styled with the active Solarized theme and font size."""
    theme = get_active_theme()
    font_size = get_font_size()
    tab_font_size = max(8, font_size - 2)

    # Common border settings matching `new_window normal 1px` & `hide_edge_borders smart`
    border_theme: dict[str, Any] = {
        "border_focus": theme.cfbg,
        "border_normal": theme.cubg,
        "border_width": 1,
        "single_border_width": 0,  # `hide_edge_borders smart`
        "margin": 0,
    }

    return [
        # Default layout: Max (matches i3's `workspace_layout tabbed` when paired with bar TaskList)
        layout.Max(
            name="max",
            border_focus=theme.cfbg,
            border_normal=theme.cubg,
            border_width=0,
        ),
        # Columns: dynamic h/v splits and column stacking (closest to i3 split & stacking containers)
        layout.Columns(
            name="columns",
            border_focus_stack=theme.cfind,
            border_normal_stack=theme.cubg,
            border_on_single=False,
            insert_position=1,
            **border_theme,
        ),
        # Stack: vertical stack layout (triggered via Mod4+i `layout stacking`)
        layout.Stack(
            name="stack",
            num_stacks=1,
            **border_theme,
        ),
        # TreeTab: sidebar tabs with full window titles
        layout.TreeTab(
            name="treetab",
            font=FONT_FAMILY,
            fontsize=tab_font_size,
            bg_color=theme.background,
            active_bg=theme.wfbg,
            active_fg=theme.wftxt,
            inactive_bg=theme.wibg,
            inactive_fg=theme.witxt,
            urgent_bg=theme.wubg,
            urgent_fg=theme.wutxt,
            panel_width=220,
            sections=["Windows"],
            section_fontsize=tab_font_size,
            section_fg=theme.watxt,
        ),
    ]


def build_floating_layout() -> layout.Floating:
    """Build floating layout matching `new_float normal 3px` & `3-window-settings.conf`."""
    theme = get_active_theme()
    return layout.Floating(
        border_focus=theme.cfbg,
        border_normal=theme.cubg,
        border_width=3,  # `new_float normal 3px`
        float_rules=[
            *layout.Floating.default_float_rules,
            Match(wm_class="confirmreset"),  # gitk
            Match(wm_class="makebranch"),  # gitk
            Match(wm_class="maketag"),  # gitk
            Match(wm_class="ssh-askpass"),  # ssh-askpass
            Match(title="branchdialog"),  # gitk
            Match(title="pinentry"),  # GPG key password entry
            # From 3-window-settings.conf:
            Match(wm_class="xfdesktop"),
        ],
    )
