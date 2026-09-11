"""Kirish sahifasini qo'pol kuch (brute-force) hujumidan himoya qilish.

NEGA KERAK: saytda 1100 dan ortiq hisob bor va `/admin/` paneli ochiq. Django
o'zi urinishlar sonini cheklamaydi — ya'ni hech qanday himoyasiz robot soatiga
minglab parolni sinab ko'rishi mumkin, va bu hech qayerda ko'rinmaydi ham.

QANDAY ISHLAYDI: faqat kirish sahifalariga kelgan POST so'rovlari sanaladi.
Muvaffaqiyatli kirish har doim boshqa sahifaga yo'naltiradi (302), muvaffaqiyatsizi
esa o'sha sahifani xato bilan qayta chizadi (200) — shu farq bo'yicha ajratiladi.
Chegara oshsa IP vaqtincha 429 oladi va muvaffaqiyatli kirish hisobni nolga qaytaradi.

CHEGARALAR ATAYLAB YUMSHOQ: bir maktabning barcha o'quvchilari bitta tashqi IP
ostida bo'lishi mumkin, shuning uchun oddiy kirish uchun chegara yuqori (30).
`/admin/` uchun esa qattiq (10): xodim atigi ikkita va ular parolini biladi.
Robot baribir minglab urinish qiladi — ikkala chegaraga ham bemalol tushadi.

Hisob Django keshida turadi (standart: xotira). Server qayta ishga tushsa
nolga qaytadi — bu yetarli, chunki hujum uzluksiz bo'ladi.
"""

import time

from django.core.cache import cache
from django.http import HttpResponse

# (yo'l, chegara, oyna_soniya, bloklash_soniya)
QOIDALAR = (
    ('/admin/login/', 10, 600, 900),   # xodim paneli — qattiq
    ('/login',        30, 600, 600),   # oddiy foydalanuvchi — yumshoq
)

# Bloklangan IP ga qaytariladigan javob (sodda matn — shablon kerak emas).
XABAR = (
    "Juda ko'p urinish bo'ldi. Xavfsizlik uchun kirish vaqtincha to'xtatildi. "
    "Iltimos, 10-15 daqiqadan keyin qayta urinib ko'ring."
)


def _mijoz_ip(sorov):
    """So'rov kelgan IP.

    `X-Forwarded-For` ga FAQAT ishonchli proksi orqasida ishonamiz
    (`SECURE_PROXY_SSL_HEADER` o'rnatilgan bo'lsa). Aks holda hujumchi bu
    sarlavhani o'zi yozib, har safar boshqa IP bo'lib ko'rinishi va
    cheklovni butunlay aylanib o'tishi mumkin edi.

    Proksi orqasida ham faqat OXIRGI qiymat olinadi. nginx
    (`$proxy_add_x_forwarded_for`) mijoz yuborgan sarlavhani saqlab, haqiqiy
    IP ni oxiriga qo'shadi: `X-Forwarded-For: soxta` yuborgan hujumchi
    `soxta, 1.2.3.4` bo'lib keladi. Birinchi qiymat mijozniki — uni har
    safar almashtirib, cheklovni aylanib o'tish mumkin edi. Oxirgisini nginx
    o'zi yozadi, uni soxtalashtirib bo'lmaydi (oldinda bitta proksi bor).
    """
    from django.conf import settings

    if getattr(settings, 'SECURE_PROXY_SSL_HEADER', None):
        oldinga = sorov.META.get('HTTP_X_FORWARDED_FOR', '')
        if oldinga:
            return oldinga.split(',')[-1].strip()
    return sorov.META.get('REMOTE_ADDR', '?')


def _qoida(yol):
    for boshi, chegara, oyna, blok in QOIDALAR:
        if yol.startswith(boshi):
            return boshi, chegara, oyna, blok
    return None


class KirishCheklovi:
    """Kirish urinishlarini sanaydigan oraliq qatlam (middleware)."""

    def __init__(self, keyingi):
        self.keyingi = keyingi

    def __call__(self, sorov):
        qoida = _qoida(sorov.path) if sorov.method == 'POST' else None
        if qoida is None:
            return self.keyingi(sorov)

        boshi, chegara, oyna, blok = qoida
        ip = _mijoz_ip(sorov)
        kalit = f'kirish:{boshi}:{ip}'
        blok_kaliti = f'blok:{boshi}:{ip}'

        tugash = cache.get(blok_kaliti)
        if tugash and tugash > time.time():
            return HttpResponse(XABAR, status=429, content_type='text/plain; charset=utf-8')

        javob = self.keyingi(sorov)

        # 302 — kirish muvaffaqiyatli bo'lib, boshqa sahifaga yo'naltirildi.
        if 300 <= javob.status_code < 400:
            cache.delete(kalit)
            return javob

        urinish = (cache.get(kalit) or 0) + 1
        cache.set(kalit, urinish, oyna)
        if urinish >= chegara:
            cache.set(blok_kaliti, time.time() + blok, blok)
            cache.delete(kalit)
            import logging
            logging.getLogger('django.security').warning(
                'Kirish cheklovi ishga tushdi: %s uchun %s (%s urinish)', boshi, ip, urinish
            )
        return javob
