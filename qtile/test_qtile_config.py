"""Unit and architectural tests for the modular Qtile configuration.

Compatible with both standard library `python3 -m unittest` and `pytest`.
Includes a lightweight `libqtile` stub so tests can run outside an X11/Qtile environment.
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import types
import unittest
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
QTILE_DIR = REPO_ROOT / "qtile"


def _install_libqtile_stub() -> dict[str, list[Any]]:
    """Install a minimal stub of `libqtile` into `sys.modules` if not installed."""
    hook_registry: dict[str, list[Any]] = {
        "startup": [],
        "setgroup": [],
        "client_new": [],
        "client_killed": [],
    }

    libqtile_mod = types.ModuleType("libqtile")

    class _Subscribe:
        def startup(self, func: Any) -> Any:
            hook_registry["startup"].append(func)
            return func

        def setgroup(self, func: Any) -> Any:
            hook_registry["setgroup"].append(func)
            return func

        def client_new(self, func: Any) -> Any:
            hook_registry["client_new"].append(func)
            return func

        def client_killed(self, func: Any) -> Any:
            hook_registry["client_killed"].append(func)
            return func

    hook_mod = types.ModuleType("libqtile.hook")
    hook_mod.subscribe = _Subscribe()  # type: ignore[attr-defined]
    hook_mod.clear = lambda: {k: v.clear() for k, v in hook_registry.items()}  # type: ignore[attr-defined]
    hook_mod.registry = hook_registry  # type: ignore[attr-defined]

    class _BaseObj:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            self.args = args
            self.kwargs = kwargs
            for k, v in kwargs.items():
                setattr(self, k, v)

    class Key(_BaseObj):
        def __init__(
            self, modifiers: list[str], key: str, *commands: Any, desc: str = ""
        ) -> None:
            super().__init__(modifiers, key, *commands, desc=desc)
            self.modifiers = modifiers
            self.key = key
            self.commands = commands
            self.desc = desc

    class KeyChord(_BaseObj):
        def __init__(
            self,
            modifiers: list[str],
            key: str,
            submappings: list[Key],
            mode: bool = False,
            name: str = "",
        ) -> None:
            super().__init__(modifiers, key, submappings, mode=mode, name=name)
            self.modifiers = modifiers
            self.key = key
            self.submappings = submappings
            self.mode = mode
            self.name = name

    class Group(_BaseObj):
        def __init__(self, name: str, **kwargs: Any) -> None:
            super().__init__(name, **kwargs)
            self.name = name

    class DropDown(_BaseObj):
        def __init__(self, name: str, cmd: str, **kwargs: Any) -> None:
            super().__init__(name, cmd, **kwargs)
            self.name = name
            self.cmd = cmd

    class ScratchPad(Group):
        def __init__(
            self, name: str, dropdowns: list[DropDown], **kwargs: Any
        ) -> None:
            super().__init__(name, **kwargs)
            self.dropdowns = {d.name: d for d in dropdowns}

    class Match(_BaseObj):
        def compare(self, window: Any) -> bool:
            return False

    class Screen(_BaseObj):
        pass

    class Mouse(_BaseObj):
        pass

    class Drag(Mouse):
        pass

    class Click(Mouse):
        pass

    config_mod = types.ModuleType("libqtile.config")
    for cls in (
        Key,
        KeyChord,
        Group,
        DropDown,
        ScratchPad,
        Match,
        Screen,
        Mouse,
        Drag,
        Click,
    ):
        setattr(config_mod, cls.__name__, cls)

    class _LazyCall:
        def __getattr__(self, name: str) -> Any:
            return _LazyCall()

        def __getitem__(self, item: Any) -> Any:
            return _LazyCall()

        def __call__(self, *args: Any, **kwargs: Any) -> Any:
            return _LazyCall()

        def function(self, func: Any) -> Any:
            def _wrapper(*args: Any, **kwargs: Any) -> Any:
                return (func, args, kwargs)

            _wrapper.func = func  # type: ignore[attr-defined]
            return _wrapper

    lazy_mod = types.ModuleType("libqtile.lazy")
    lazy_mod.lazy = _LazyCall()  # type: ignore[attr-defined]

    class _LayoutType(_BaseObj):
        default_float_rules: list[Any] = []

    layout_mod = types.ModuleType("libqtile.layout")
    for name in ("Max", "Columns", "Stack", "TreeTab", "Floating"):
        setattr(layout_mod, name, type(name, (_LayoutType,), {}))

    bar_mod = types.ModuleType("libqtile.bar")
    bar_mod.Bar = type("Bar", (_BaseObj,), {})  # type: ignore[attr-defined]

    widget_mod = types.ModuleType("libqtile.widget")
    for wname in (
        "GroupBox",
        "Chord",
        "TaskList",
        "GenPollText",
        "TextBox",
        "Clock",
        "Systray",
    ):
        setattr(widget_mod, wname, type(wname, (_BaseObj,), {}))

    libqtile_mod.hook = hook_mod  # type: ignore[attr-defined]
    libqtile_mod.config = config_mod  # type: ignore[attr-defined]
    libqtile_mod.lazy = lazy_mod  # type: ignore[attr-defined]
    libqtile_mod.layout = layout_mod  # type: ignore[attr-defined]
    libqtile_mod.bar = bar_mod  # type: ignore[attr-defined]
    libqtile_mod.widget = widget_mod  # type: ignore[attr-defined]
    libqtile_mod.qtile = None  # type: ignore[attr-defined]

    sys.modules["libqtile"] = libqtile_mod
    sys.modules["libqtile.hook"] = hook_mod
    sys.modules["libqtile.config"] = config_mod
    sys.modules["libqtile.lazy"] = lazy_mod
    sys.modules["libqtile.layout"] = layout_mod
    sys.modules["libqtile.bar"] = bar_mod
    sys.modules["libqtile.widget"] = widget_mod

    return hook_registry


HOOK_REGISTRY = _install_libqtile_stub()


def load_config_like_qtile(
    config_path: Path = QTILE_DIR / "config.py",
) -> types.ModuleType:
    """Replicate `libqtile.confreader.Config.load()` execution of `config.py`."""
    name = config_path.stem
    spec = importlib.util.spec_from_file_location(name, config_path)
    assert spec is not None and spec.loader is not None
    config_mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = config_mod
    spec.loader.exec_module(config_mod)
    return config_mod


class TestQtileConfigArchitecture(unittest.TestCase):
    """Test suite verifying Qtile config loading, reload behavior, and state management."""

    def setUp(self) -> None:
        from libqtile import hook

        hook.clear()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_state_file = Path(self.temp_dir.name) / "state.json"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_initial_config_load_exports_required_symbols(self) -> None:
        """Verify config.py exports all required Qtile attributes."""
        cfg = load_config_like_qtile()
        self.assertTrue(hasattr(cfg, "keys") and len(cfg.keys) > 20)
        self.assertTrue(hasattr(cfg, "groups") and len(cfg.groups) == 12)
        self.assertTrue(hasattr(cfg, "layouts") and len(cfg.layouts) == 4)
        self.assertTrue(hasattr(cfg, "floating_layout"))
        self.assertTrue(hasattr(cfg, "screens") and len(cfg.screens) == 2)
        self.assertTrue(hasattr(cfg, "mouse") and len(cfg.mouse) == 3)
        self.assertEqual(cfg.follow_mouse_focus, False)
        self.assertEqual(cfg.cursor_warp, True)
        self.assertEqual(cfg.wmname, "LG3D")

    def test_reload_config_re_registers_hooks_and_preserves_window_tracker(self) -> None:
        """Simulating Qtile's `reload_config()` must re-register hooks in submodules
        (`startup.py`, `groups.py`) while preserving live `groups.TRACKER` state.
        """
        from libqtile import hook

        # 1. Initial load registers hooks
        load_config_like_qtile()
        self.assertEqual(len(HOOK_REGISTRY["startup"]), 1)
        self.assertEqual(len(HOOK_REGISTRY["setgroup"]), 1)
        self.assertEqual(len(HOOK_REGISTRY["client_new"]), 1)
        self.assertEqual(len(HOOK_REGISTRY["client_killed"]), 1)

        # Track a sticky window ID before reload
        import groups

        groups.TRACKER.sticky_windows.add(4242)

        # 2. Simulate Qtile's `reload_config()`: Qtile clears hook subscriptions,
        #    then re-executes `config.py` while submodules are already in `sys.modules`.
        hook.clear()
        self.assertEqual(len(HOOK_REGISTRY["startup"]), 0)

        load_config_like_qtile()

        # Verify all submodule hooks were re-registered
        self.assertEqual(len(HOOK_REGISTRY["startup"]), 1)
        self.assertEqual(len(HOOK_REGISTRY["setgroup"]), 1)
        self.assertEqual(len(HOOK_REGISTRY["client_new"]), 1)
        self.assertEqual(len(HOOK_REGISTRY["client_killed"]), 1)

        # Verify live sticky window state survived submodule reload
        self.assertIn(4242, groups.TRACKER.sticky_windows)
        groups.TRACKER.sticky_windows.discard(4242)

    def test_runtime_state_theme_bar_and_font_scaling(self) -> None:
        """Verify RuntimeState persistence for theme, bar position, and font scaling."""
        load_config_like_qtile()
        import settings

        # Default state
        state = settings.RuntimeState.load(self.temp_state_file)
        self.assertEqual(state.theme, "dark")
        self.assertEqual(state.bar_position, "bottom")
        self.assertEqual(state.font_size, 14)
        self.assertEqual(state.bar_font_size, 15)

        # Cycle theme dark -> light -> dark
        new_theme = settings.cycle_theme(1, path=self.temp_state_file)
        self.assertEqual(new_theme, "light")
        self.assertEqual(settings.get_active_theme(self.temp_state_file).name, "light")

        # Bar position top
        settings.set_bar_position("top", path=self.temp_state_file)
        self.assertEqual(settings.get_bar_position(self.temp_state_file), "top")

        # Scale font size +2pt, then clamp at MAX_FONT_SIZE, then reset
        f_size, b_size = settings.adjust_font_size(2, path=self.temp_state_file)
        self.assertEqual((f_size, b_size), (16, 17))
        f_size, b_size = settings.adjust_font_size(100, path=self.temp_state_file)
        self.assertEqual((f_size, b_size), (settings.MAX_FONT_SIZE, settings.MAX_FONT_SIZE))
        f_size, b_size = settings.reset_font_size(path=self.temp_state_file)
        self.assertEqual((f_size, b_size), (14, 15))

    def test_window_title_icon_formatting(self) -> None:
        """Verify window title icon rules match 3-window-settings.conf."""
        load_config_like_qtile()
        import groups

        class _DummyWin:
            def __init__(self, wm_classes: list[str]) -> None:
                self._classes = wm_classes

            def get_wm_class(self) -> list[str]:
                return self._classes

        self.assertEqual(
            groups.format_window_title(_DummyWin(["jetbrains-pycharm"]), "i3config"),
            "   i3config",
        )
        # Title rule "Write:.* Thunderbird" overrides class rule "Thunderbird"
        self.assertEqual(
            groups.format_window_title(
                _DummyWin(["Thunderbird"]), "Write: Hello - Thunderbird"
            ),
            "   Write: Hello - Thunderbird",
        )


if __name__ == "__main__":
    unittest.main()
