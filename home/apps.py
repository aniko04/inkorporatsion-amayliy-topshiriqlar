import os
import sys

from django.apps import AppConfig
from django.core.checks import Warning, register


class HomeConfig(AppConfig):
    name = 'home'

    def ready(self):
        register(_rasmli_test_rasmlari)
        register(_diktant_rasmlari)
        register(_qalamdon_fayllari)
        register(_xonqizi_fayllari)
        _avtomatik_zaxira()


def _avtomatik_zaxira():
    """Sayt ishga tushganda bazadan sutkalik zaxira nusxa oladi.

    Baza git'da yo'q (parollar va shaxsiy ma'lumot bor), ya'ni u o'chsa hech
    narsa tiklab bera olmaydi. Shu sababli nusxa olish qo'lga tashlab
    qo'yilmagan — server har ko'tarilganda o'zi tekshiradi.

    Faqat sayt HAQIQATAN xizmat qilayotganda ishlaydi: `migrate`, `shell`,
    `check` kabi buyruqlarda ham nusxa olinsa, jild keraksiz to'lib ketardi.
    `RUN_MAIN` sharti esa `runserver` ning avtoyuklagichi jarayonni ikki marta
    ishga tushirishi uchun — nusxa ikki marta olinmasin.

    Xato bo'lsa jimgina o'tib ketadi (`kerak_bolsa_zaxira` ichida) — zaxira
    olinmagani saytning ochilmasligiga sabab bo'lmasligi kerak.
    """
    buyruq = sys.argv[1] if len(sys.argv) > 1 else ''
    xizmat_qilyapti = buyruq == 'runserver' or 'waitress' in sys.argv[0].lower()
    if not xizmat_qilyapti:
        return
    if buyruq == 'runserver' and '--noreload' not in sys.argv and not os.environ.get('RUN_MAIN'):
        return          # avtoyuklagichning ota-jarayoni — bola jarayon oladi

    from . import zaxira
    nusxa = zaxira.kerak_bolsa_zaxira()
    if nusxa is not None:
        print(f'[zaxira] baza nusxasi olindi: {nusxa.name}')


def _rasmli_test_rasmlari(app_configs, **kwargs):
    """«Rasmli test» rasmlari joyidami — `manage.py check` tekshiradi.

    Rasmlar Worddan skript bilan yasaladi; bittasi tushib qolsa sahifada
    jimgina buzuq rasm chiqadi, shuning uchun uni shu yerda ushlaymiz.
    """
    from . import rasmli_test
    yoq = rasmli_test.yetishmagan_rasmlar()
    if not yoq:
        return []
    return [Warning(
        "«Rasmli test» rasmlari yetishmayapti: " + ', '.join(yoq),
        hint="static/img/rasmli-test/ ni Worddan qayta yasang.",
        id='home.W001',
    )]


def _diktant_rasmlari(app_configs, **kwargs):
    """«Texnologik diktantlar» rasmlari joyidami — W001 bilan bir xil sabab.

    64 ta rasmdan bittasi tushib qolsa, o'quvchi javob berolmaydigan
    topshiriq paydo bo'ladi; shuning uchun sahifaga chiqishdan oldin
    `manage.py check` da ushlaymiz.
    """
    from . import diktant
    yoq = diktant.yetishmagan_rasmlar()
    if not yoq:
        return []
    return [Warning(
        "«Texnologik diktantlar» rasmlari yetishmayapti: " + ', '.join(yoq),
        hint="static/img/diktant/ ni Worddan qayta yasang.",
        id='home.W002',
    )]


def _qalamdon_fayllari(app_configs, **kwargs):
    """«Qalamdon» xaritasining rasm va videolari joyidami.

    Videolar `media/` da turadi va hech qanday yig'ish bosqichidan
    o'tmaydi — ko'chirilmay qolsa sahifada bo'sh pleyer qoladi, xato esa
    hech qayerda ko'rinmaydi. Shuning uchun ular ham shu yerda sanaladi.
    """
    from . import qalamdon
    yoq = qalamdon.yetishmagan_fayllar()
    if not yoq:
        return []
    return [Warning(
        "«Qalamdon» xaritasi fayllari yetishmayapti: " + ', '.join(yoq),
        hint="static/img/qalamdon/ va media/xarita/qalamdon/ ni tekshiring.",
        id='home.W003',
    )]


def _xonqizi_fayllari(app_configs, **kwargs):
    """«Xonqizi» xaritasining rasm va videolari joyidami — W003 bilan bir xil sabab."""
    from . import xonqizi
    yoq = xonqizi.yetishmagan_fayllar()
    if not yoq:
        return []
    return [Warning(
        "«Xonqizi» xaritasi fayllari yetishmayapti: " + ', '.join(yoq),
        hint="static/img/xonqizi/ va media/xarita/xonqizi/ ni tekshiring.",
        id='home.W004',
    )]
