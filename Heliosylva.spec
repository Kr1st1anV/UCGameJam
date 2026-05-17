# PyInstaller spec — single-file Windows build
# Run: pyinstaller Heliosylva.spec
# Output: dist/Heliosylva.exe (one file; assets unpack to temp at launch)

import os

block_cipher = None

project_dir = os.path.dirname(os.path.abspath(SPEC))

asset_dirs = (
    'assets',
    'bground',
    'buttons',
    'cutscenes',
    'fonts',
    'mobs',
    'music',
    'startscreen',
    'tiles',
    'towers',
    'tree_health',
)

datas = [
    (os.path.join(project_dir, name), name)
    for name in asset_dirs
    if os.path.isdir(os.path.join(project_dir, name))
]

a = Analysis(
    [os.path.join(project_dir, 'main.py')],
    pathex=[project_dir],
    binaries=[],
    datas=datas,
    hiddenimports=['pygame', 'numpy', 'maps', 'paths', 'start_screen'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Heliosylva',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
