# Lessons Learned

## Path Handling
- **Encoding:** Windows file paths can contain non-ASCII characters (e.g., Vietnamese). Python's `os.walk` and `os.scandir` handle unicode correctly, but passing paths via `sys.argv` or displaying them in error messages might require care.
- **Long Paths:** Windows has a 260-character path limit unless `\\?\` prefix is used. Updated code to automatically prepend `\\?\` for long paths when using `os.path` functions and `send2trash`.
- **Error Messages:** Raw `OSError` messages can be confusing or garbled. Always wrap file operations in `try-except` blocks and provide user-friendly messages with the full path context.

## Packaging & Distribution
- **Inno Setup:** Professional Windows installers are best created using Inno Setup. It provides built-in support for shortcuts, registry changes (context menu), and path updates.
- **Portable Builds:** PyInstaller is reliable for creating standalone executables (`--onefile`).
- **Dependencies:** Installer building requires `iscc` (Inno Setup Compiler) to be installed on the build machine. The `build_installer.py` script checks for this and provides instructions if missing.
