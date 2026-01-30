# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('src/resources', 'src/resources')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PySide6.QtNetwork', 'PySide6.QtSql', 'PySide6.QtXml', 'PySide6.QtTest', 'PySide6.QtDBus', 'PySide6.QtWebEngine', 'PySide6.QtPdf', 'PySide6.QtMultimedia', 'PySide6.QtCharts', 'PySide6.QtOpenGL', 'PySide6.QtQml', 'PySide6.QtQuick', 'PySide6.Qt3D', 'PySide6.QtBluetooth', 'PySide6.QtPositioning', 'PySide6.QtSensors', 'PySide6.QtSerialPort', 'PySide6.QtWebChannel', 'PySide6.QtWebSockets', 'PySide6.QtRemoteObjects', 'PySide6.QtDesigner', 'PySide6.QtHelp'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='1.1.0 test',
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
