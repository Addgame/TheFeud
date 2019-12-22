# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['src\\control.py'],
             pathex=['C:\\Users\\Adam\\Documents\\Programming\\FamilyFeud'],
             binaries=[],
             datas=[('assets', 'assets'), ('surveys/example.survey', 'surveys')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='Family Feud Game',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False , icon='assets\\images\\icon.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='Family Feud Game')
