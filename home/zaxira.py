"""Ma'lumotlar bazasining zaxira nusxasi.

Baza (`db.sqlite3`) git'ga KIRMAYDI — ichida parol hash'lari va 1100 dan ortiq
foydalanuvchining shaxsiy ma'lumoti bor. Ya'ni uni git tiklab bera olmaydi:
o'chsa, butunlay yo'qoladi. Shu modul uni himoya qiladi.

Ikki yo'l bilan ishlaydi:
  • `python manage.py zaxira` — qo'lda;
  • sayt ishga tushganda avtomatik (sutkada bir marta) — `home/apps.py` chaqiradi.

NEGA ODDIY `cp` EMAS: baza WAL rejimida ishlaydi (`core/settings.py` ga qarang),
ya'ni oxirgi yozuvlar `db.sqlite3-wal` faylida turishi mumkin. Faylni shunchaki
nusxalash o'sha yozuvlarni tashlab ketadi. SQLite'ning o'z `.backup` amali esa
sayt ishlab turganda ham butun va izchil nusxa oladi.
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from django.conf import settings

# Zaxira nusxalar baza yonida — ma'lumot jildida (`core/settings.py`,
# MALUMOT_JILDI; Docker'da volume ichida). `.gitignore` da — git'ga tushmaydi.
ZAXIRA_JILDI = Path(getattr(settings, 'MALUMOT_JILDI', settings.BASE_DIR)) / 'zaxira'

# Nechta nusxa saqlanadi (eskisi o'chib boradi).
ENG_KOP_NUSXA = 14


def _baza_yoli():
    return Path(settings.DATABASES['default']['NAME'])


def zaxira_ol(jild=None, eng_kop=ENG_KOP_NUSXA):
    """Bazadan butun nusxa oladi va yaratilgan fayl yo'lini qaytaradi.

    Sayt ishlab turganda ham xavfsiz. Eski nusxalar `eng_kop` dan oshsa,
    eng eskisidan boshlab o'chiriladi.
    """
    manba = _baza_yoli()
    if not manba.exists():
        raise FileNotFoundError(f'Baza topilmadi: {manba}')

    jild = Path(jild) if jild else ZAXIRA_JILDI
    jild.mkdir(parents=True, exist_ok=True)
    nusxa = jild / f'db_{datetime.now():%Y-%m-%d_%H%M%S}.sqlite3'

    # Manbani faqat o'qish uchun ochamiz — nusxa olish jarayoni saytga
    # yozishga xalaqit bermasin.
    ichki = sqlite3.connect(f'file:{manba}?mode=ro', uri=True)
    tashqi = sqlite3.connect(nusxa)
    try:
        with tashqi:
            ichki.backup(tashqi)
    finally:
        tashqi.close()
        ichki.close()

    _eskilarini_tozala(jild, eng_kop)
    return nusxa


def _eskilarini_tozala(jild, eng_kop):
    nusxalar = sorted(jild.glob('db_*.sqlite3'))
    for eski in nusxalar[:-eng_kop] if eng_kop > 0 else []:
        try:
            eski.unlink()
        except OSError:
            pass


def oxirgi_nusxa(jild=None):
    """Eng so'nggi zaxira fayli (yo'q bo'lsa None)."""
    jild = Path(jild) if jild else ZAXIRA_JILDI
    nusxalar = sorted(jild.glob('db_*.sqlite3')) if jild.exists() else []
    return nusxalar[-1] if nusxalar else None


def kerak_bolsa_zaxira(oraliq_soat=24):
    """Oxirgi nusxa eskirgan bo'lsa yangisini oladi.

    Sayt ishga tushganda chaqiriladi, shuning uchun HECH QACHON xato
    ko'tarmaydi: zaxira olinmagani saytning ishlamasligiga sabab bo'lmasligi
    kerak. Nusxa olingan bo'lsa uning yo'lini, aks holda None qaytaradi.
    """
    try:
        oxirgi = oxirgi_nusxa()
        if oxirgi is not None:
            yosh = datetime.now() - datetime.fromtimestamp(oxirgi.stat().st_mtime)
            if yosh < timedelta(hours=oraliq_soat):
                return None
        return zaxira_ol()
    except Exception:
        return None
