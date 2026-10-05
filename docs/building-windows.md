# Building on Windows

The project uses PyInstaller in the `release` extra. The checked-in `nyaaapi-gui.spec` collects the Qt platform plugins and bundled SVG icon and produces a windowed, one-folder build.

```powershell
python -m pip install -e ".[release,dev]"
pyinstaller --clean --noconfirm nyaaapi-gui.spec
Compress-Archive -Path dist\NyaaAPI-GUI\* -DestinationPath dist\NyaaAPI-GUI-windows-x64.zip -Force
```

Test the result on a Windows account without the source checkout or development environment. Keep the full `dist/NyaaAPI-GUI` folder together; Qt plugins and runtime DLLs are included alongside the executable.
