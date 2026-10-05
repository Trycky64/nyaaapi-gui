from __future__ import annotations

from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules

root = Path.cwd()
src = root / "src"
icon_data = (str(src / "nyaaapi_gui" / "resources" / "icon.svg"), "nyaaapi_gui/resources")
hidden_imports = [
    "PySide6.QtSvg",
    "PySide6.QtSvgWidgets",
    *collect_submodules("qbittorrentapi"),
]

a = Analysis(
    [str(root / "packaging" / "windows_entry.py")],
    pathex=[str(src)],
    binaries=[],
    datas=[icon_data],
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter"],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="NyaaAPI-GUI",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    icon=str(root / "assets" / "nyaaapi-gui.ico"),
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="NyaaAPI-GUI",
)
