# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['macos_wrapper.py'],
    pathex=[],
    binaries=[],
    datas=[('template_dashboard.html', '.'), ('template_dashboard.css', '.'), ('dashboard.js', '.'), ('dashboard-utils.js', '.'), ('readme.md', '.'), ('ai_analyzer.py', '.'), ('devices.py', '.'), ('dialog_utils.py', '.'), ('file_utils.py', '.'), ('log_processor.py', '.'), ('tag_validator.py', '.'), ('ui_theme.py', '.'), ('main.py', '.')],
    hiddenimports=['tkinter', 'pandas', 'matplotlib', 'numpy'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='TagValidator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TagValidator',
)
app = BUNDLE(
    coll,
    name='TagValidator.app',
    icon=None,
    bundle_identifier=None,
)
