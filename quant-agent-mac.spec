# -*- mode: python ; coding: utf-8 -*-
"""
Mac 平台 PyInstaller 配置文件
用于将 quant-agent 打包成 macOS .app bundle
"""

from PyInstaller.utils.hooks import collect_all

datas = []
binaries = []
hiddenimports = [
    'agent', 'agent.main', 'agent.api', 'agent.api.health',
    'agent.core', 'agent.core.config', 'agent.utils', 'agent.utils.logger',
    'uvicorn', 'uvicorn.logging', 'uvicorn.loops', 'uvicorn.loops.auto',
    'uvicorn.protocols', 'uvicorn.protocols.http', 'uvicorn.protocols.http.auto',
    'uvicorn.protocols.http.h11_impl', 'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto', 'uvicorn.protocols.websockets.wsproto',
    'uvicorn.protocols.websockets.wsproto_impl', 'uvicorn.lifespan',
    'uvicorn.lifespan.on', 'fastapi', 'pydantic', 'pydantic_settings',
    'starlette', 'starlette.responses', 'starlette.routing'
]

tmp_ret = collect_all('uvicorn')
datas += tmp_ret[0]
binaries += tmp_ret[1]
hiddenimports += tmp_ret[2]

a = Analysis(
    ['agent/main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    name='quant-agent',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Mac上隐藏终端窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='quant-agent',
)

# BUNDLE 是 Mac 平台特有的，创建 .app 应用包
app = BUNDLE(
    coll,
    name='QuantAgent.app',
    icon=None,  # 可选：添加应用图标 'icon.icns'
    bundle_identifier='com.fastbull.quantagent',  # 唯一标识符
    info_plist={
        'CFBundleName': 'Quant Agent',
        'CFBundleDisplayName': 'Quant Agent',
        'CFBundleVersion': '0.1.0',
        'CFBundleShortVersionString': '0.1.0',
        'NSHighResolutionCapable': 'True',
        'LSBackgroundOnly': 'False',  # False = 显示在Dock
        'LSUIElement': 'False',  # False = 显示菜单栏

        # 注册 URL Scheme - 关键配置！
        # 这样Web端可以通过 quant-agent://launch 唤起应用
        'CFBundleURLTypes': [
            {
                'CFBundleURLName': 'Quant Agent Protocol',
                'CFBundleURLSchemes': ['quant-agent'],
            }
        ],

        # 权限声明（如需要）
        'NSAppleEventsUsageDescription': 'Quant Agent needs to handle URL schemes.',
    },
)
