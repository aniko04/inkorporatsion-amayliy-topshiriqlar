# -*- coding: utf-8 -*-
"""
`.exe` ni yig'ish skripti.

Ishlatish (loyiha ildizidan):

    ilova/qurish-env/Scripts/python.exe ilova/qur.py

Natija: `ilova/dist/Inkorporatsion amaliy topshiriqlar.exe` — Python
o'rnatilmagan Windows kompyuterlarida ham ishlaydigan yagona fayl.

Qurish muhitini noldan tiklash kerak bo'lsa:

    py -3.11 -m venv ilova/qurish-env
    ilova/qurish-env/Scripts/python.exe -m pip install pywebview pyinstaller
"""

import os
import shutil
import subprocess
import sys

BU_YER = os.path.dirname(os.path.abspath(__file__))
NOM = "Inkorporatsion amaliy topshiriqlar"

# .exe xossalarida (o'ng tugma → Properties → Details) ko'rinadigan ma'lumot.
# Bo'sh qoldirilsa Windows faylni «noma'lum nashriyot» deb ko'rsatadi.
VERSIYA_MATNI = """
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0), prodvers=(1, 0, 0, 0),
    mask=0x3f, flags=0x0, OS=0x40004, fileType=0x1, subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable('040904B0', [
        StringStruct('CompanyName', 'Jo\\'rayeva Dilnoz Raxmidinovna'),
        StringStruct('FileDescription', 'Inkorporatsion amaliy topshiriqlar'),
        StringStruct('FileVersion', '1.0.0.0'),
        StringStruct('InternalName', 'inkorporatsion'),
        StringStruct('LegalCopyright', 'Inkorporatsion amaliy topshiriqlar platformasi'),
        StringStruct('OriginalFilename', 'Inkorporatsion amaliy topshiriqlar.exe'),
        StringStruct('ProductName', 'Inkorporatsion amaliy topshiriqlar'),
        StringStruct('ProductVersion', '1.0.0.0')])
    ]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
"""


def main():
    ish = os.path.join(BU_YER, 'build')
    chiqish = os.path.join(BU_YER, 'dist')
    os.makedirs(ish, exist_ok=True)

    versiya_fayli = os.path.join(ish, 'versiya.txt')
    with open(versiya_fayli, 'w', encoding='utf-8') as f:
        f.write(VERSIYA_MATNI)

    buyruq = [
        sys.executable, '-m', 'PyInstaller',
        '--noconfirm',
        '--clean',
        '--onefile',            # bitta fayl — ko'chirib yurish oson
        '--windowed',           # qora konsol oynasi chiqmasin
        '--name', NOM,
        '--icon', os.path.join(BU_YER, 'belgi.ico'),
        '--version-file', versiya_fayli,
        '--distpath', chiqish,
        '--workpath', ish,
        '--specpath', ish,
        # WebView2 ni ishga tushiruvchi .NET ko'prigi — hook o'zi topadi,
        # lekin onefile rejimida ba'zan tushib qoladi, shuning uchun ochiq
        # yozib qo'yilgan.
        '--collect-all', 'webview',
        '--collect-all', 'clr_loader',
        '--hidden-import', 'pythonnet',
        # Kerak emas, hajmni bekorga oshiradi.
        '--exclude-module', 'tkinter',
        '--exclude-module', 'unittest',
        '--exclude-module', 'pydoc',
        '--exclude-module', 'doctest',
        os.path.join(BU_YER, 'ilova.py'),
    ]

    print('>>>', ' '.join(buyruq), '\n')
    natija = subprocess.run(buyruq)
    if natija.returncode != 0:
        sys.exit(natija.returncode)

    exe = os.path.join(chiqish, NOM + '.exe')
    if not os.path.exists(exe):
        print('XATO: .exe yaratilmadi')
        sys.exit(1)

    # Mijozga beriladigan papka: .exe + manzil sozlamasi + qo'llanma.
    for fayl in ('manzil.txt', 'OQING.txt'):
        shutil.copyfile(
            os.path.join(BU_YER, fayl),
            os.path.join(chiqish, fayl),
        )

    print('\nTAYYOR: %s  (%.1f MB)' % (exe, os.path.getsize(exe) / 1048576))


if __name__ == '__main__':
    main()
