"""«Xonqizi» — applikatsiya usulida xonqizi (qo'ng'izcha) yasashning
instruksion texnologik xaritasi. Tuzilishi «Qalamdon» bilan bir xil
(`home/qalamdon.py` ga qarang) — farqlari shu izohda sanab o'tilgan.

Manba: `malumotlar/texnologikxarita/xonqizi/Xonqizi Yangi.docx` — 12 bosqichli
jadval. Wordda uch mazmunli ustun bor (ketma-ketlik / ishlar tasviri / kerakli
ish anjomlari); saytda ular orasiga TO'RTINCHI — **Video** ustuni qo'shildi va
anjomlar oxiriga surildi. Word faylining o'zi o'zgartirilmagan.

**Video ustunining tartibi mijozning ko'rsatmasi:** birinchi bosqichda video
YO'Q (u ish o'rnini tayyorlash haqida), qolgan 11 bosqichga esa lavhalar
ketma-ket qo'yiladi — 2-bosqichga 1-lavha, 3-bosqichga 2-lavha va hokazo.

Lavhalar mijozning papkasida `1/`…`11/` nomli kataloglarda, katalog raqami =
ko'rsatish tartibi. Fayl nomlari chalkash (`11-1`, `12-1`, `2-1`, `51-1`,
`10-2-1`…) va katalog ichida ESKI, o'rni siljigan nusxalar ham yotibdi:
mijoz 6 ta uzun videoni 11 ta lavhaga bo'lganda avvalgi joylashuv shunday
qolgan. Bo'linish davomiylikdan aniq ko'rinadi va ikkilanishga o'rin
qoldirmaydi:

    1 (60.37s) → 11 (24.94) + 12 (35.43)
    5 (22.31s) → 51 (7.97) + 52 (14.37)
    6 (94.11s) → 61 (26.52) + 62 (28.57) + 10-1 (17.97) + 10-2 (21.11)

Ya'ni har katalogdagi ENG YANGI fayl kerakli lavha; eski nusxalar
ishlatilmaydi. `_LAVHA` da shu moslik yozib qo'yilgan — video qayta
kodlanadigan bo'lsa shu jadvalga qarang, papkadagi nomlarga emas.

**Videolar qayta kodlangan:** asl fayllar HEVC (H.265) 1080p — bu kodekni
Chrome Windowsda faqat alohida kengaytma bo'lsa o'ynatadi, Firefox esa
umuman o'ynatmaydi. Hammasi H.264 (yuv420p, 1280px, CRF 26, `+faststart`)
ga o'girilgan va ovoz izmi fayl darajasida olib tashlangan (`-an`) —
`muted` atributiga ishonib qolgandan ko'ra ovozning o'zi bo'lmagani aniq.
227 MB dan 16.8 MB ga tushdi. Qalamdondan farqli o'laroq bu lavhalarda
QORA YON YO'LLAR YO'Q (tekshirildi: chap/o'ng 0 px, toza 16:9), shuning
uchun hech biri qirqilmagan.

Rasmlar `static/img/xonqizi/` da: `qadamNN.jpg` — bosqich tasviri,
`anjomNN.jpg` — kerakli ish anjomlari (ikkalasi ham Word ichidan),
`posterNN.jpg` — lavhaning 55% idagi kadr (640px). Rasmlarda bitta
o'ziga xoslik bor: buyum QIZIL, foni oq, ya'ni JPEG ning odatdagi 4:2:0
xroma siyraklashtirishi aynan qizil chekkalarni buzadi — shuning uchun
hammasi `subsampling=0` bilan saqlangan.

Videolar `media/xarita/xonqizi/` da, `static/` da emas: WhiteNoise mp4 ni
gzip qilishga urinib, `staticfiles/` ga yana bir nusxa yozadi.
"""

from pathlib import Path

RASM_YOL = '/static/img/xonqizi/'
VIDEO_YOL = '/media/xarita/xonqizi/'
RASM_VERSIYA = 1         # rasm o'sha nom bilan almashtirilsa oshiriladi (brauzer keshi)

RASM_KATALOG = Path(__file__).resolve().parent.parent / 'static' / 'img' / 'xonqizi'
VIDEO_KATALOG = Path(__file__).resolve().parent.parent / 'media' / 'xarita' / 'xonqizi'

# Mijozning o'z iborasi (2026-09-05) — Qalamdon sahifasi bilan bir qolipda.
SARLAVHA = 'Applikatsiya usulidan foydalanib «Xonqizi» yasash texnologiyasi'
# Yo'l ko'rsatkichi va brauzer yorlig'i uchun qisqa nom (qalamdon.py ga qarang).
QISQA = '«Xonqizi»'
# Lede sarlavhani takrorlamaydi.
TAVSIF = (
    "Rangli qogʻozdan ishlash ketma-ketligi, har bosqichning tasviri va video "
    "lavhasi hamda kerakli ish anjomlari — bitta jadvalda."
)
XULOSA = (
    "Xonqizi applikatsiyasini tayyorlash jarayonida oʻquvchilarda qogʻoz bilan "
    "ishlash, geometrik shakllarni aniq chizish va qirqish, detallarni simmetrik "
    "joylashtirish hamda yopishtirish koʻnikmalari rivojlanadi. Bu amaliy faoliyat "
    "oʻquvchilarning mayda motorikasi, ijodiy fikrlashi, diqqat-eʼtibori, estetik "
    "didi va konstruktorlik qobiliyatlarini shakllantirishga xizmat qiladi. Jarayon "
    "davomida mehnat xavfsizligi qoidalariga rioya qilish, ish qurollaridan toʻgʻri "
    "foydalanish va ish joyini ozoda saqlash malakalari ham mustahkamlanadi."
)

# Ustun sarlavhalari — Qalamdon sahifasidagi bilan bir xil qisqartmalar
# (Wordda «Ishni bajarish boʻyicha amalga oshiriladigan ishlar tasviri» va
# «Kerakli ish anjomlari» deb yozilgan; uzun sarlavha ustunni siqib qo'yadi).
USTUNLAR = [
    "Ishni bajarish ketma-ketligi",
    "Ishni bajarish boʻyicha amalga oshiriladigan ishlar tasviri",
    "Video",
    "Anjomlar",
]

# Bosqich → mijozning papkasidagi lavha (katalog/fayl). Faqat hujjat uchun:
# videolar bir marta qayta kodlanib `media/xarita/xonqizi/vNN.mp4` bo'lgan.
_LAVHA = {
    2: '1/11-1.mp4', 3: '2/12-1.mp4', 4: '3/2-1.mp4', 5: '4/3-1.mp4',
    6: '5/4-1.mp4', 7: '6/51-1.mp4', 8: '7/52-1.mp4', 9: '8/61-1.mp4',
    10: '9/62-1.mp4', 11: '10/10-1-1.mp4', 12: '11/10-2-1.mp4',
}

# Lavhalar davomiyligi (soniya) — kattalashtirish oynasining sarlavhasi uchun.
# Fayldan o'qilmaydi: har sahifa ochilishida ffprobe kerak bo'lardi, videolar
# esa qayta kodlanmasa o'zgarmaydi.
_DAVOMIYLIK = {
    2: 24.9, 3: 35.4, 4: 11.1, 5: 34.1, 6: 18.2, 7: 8.0,
    8: 14.4, 9: 26.5, 10: 28.6, 11: 18.0, 12: 21.1,
}

# (bosqich, matn, video bormi)
# Matnlar Worddan o'zgartirilmasdan olingan; faqat qo'shtirnoqsimon
# apostroflar (U+2018/U+2019) sayt bo'ylab ishlatiladigan ʻ (U+02BB) ga
# keltirilgan — qalamdon.py va diktant.py da ham shunday.
_XOM = [
    (1, "Kerakli ish anjomlarini tayyorlash. Ishni boshlashdan oldin qizil, qora "
        "va oq rangli qogʻozlar, qaychi, yelim, qalam, marker, chizgʻich, aylana "
        "qoliplari hamda boshqa zarur ish qurollari ish joyiga tartibli ravishda "
        "tayyorlab qoʻyiladi.", False),
    (2, "Qizil rangli doiralarni tayyorlash. Qizil rangli qogʻozga katta aylana "
        "qolipi yordamida bir xil oʻlchamdagi ikkita doira chiziladi. Kerakli "
        "qoʻshimcha doira shakllari ham belgilanib, chiziqlar boʻylab "
        "ehtiyotkorlik bilan qirqib olinadi.", True),
    (3, "Qora rangli tana qismlarini tayyorlash. Qora rangli qogʻozga xonqizining "
        "tana va bosh qismlari uchun zarur boʻlgan katta va kichik doiralar "
        "belgilanadi. Belgilangan shakllar qaychi yordamida aniq qirqib olinadi.", True),
    (4, "Qanotlarni buklash va tana qismiga biriktirish. Tayyorlangan ikkita qizil "
        "doira teng ikkiga buklanadi. Buklama chizigʻi aniq hosil qilinib, qanotlar "
        "tana qismining chap va oʻng tomoniga simmetrik joylashtiriladi hamda yelim "
        "yordamida mahkamlanadi.", True),
    (5, "Qora tana va bosh qismini mustahkamlash. Qora rangli tana hamda bosh "
        "qismlari kompozitsiyadagi belgilangan oʻrniga joylashtiriladi. Qismlarning "
        "oʻzaro mutanosib va simmetrik holatda boʻlishiga eʼtibor berilib, yelim "
        "yordamida ehtiyotkorlik bilan biriktiriladi.", True),
    (6, "Koʻz va moʻylovlarni tayyorlash. Oq rangli qogʻozdan koʻzlar uchun kichik "
        "doiralar qirqib olinadi yoki tayyor koʻzchalar tanlanadi. Koʻzlar bosh "
        "qismiga simmetrik joylashtiriladi. Qora qogʻozdan xonqizining ikki "
        "tomonlama moʻylovlari tayyorlanadi.", True),
    (7, "Qanotlarni qora nuqtalar bilan bezash. Qora rangli qogʻozdan bir xil yoki "
        "yaqin oʻlchamdagi kichik doirachalar tayyorlanadi. Ular qizil qanotlarning "
        "yuzasiga tartibli va simmetrik ravishda joylashtirilib, yelim yordamida "
        "yopishtiriladi.", True),
    (8, "Asosiy kompozitsiyani tekshirish. Tayyorlangan xonqizi aplikatsiyasining "
        "tana, qanot va bezak qismlari oʻzaro mosligi tekshiriladi. Qanotlarning "
        "simmetrik joylashuvi, qora nuqtalarning tartibi va detallarining "
        "mustahkamligi nazorat qilinadi.", True),
    (9, "Moʻylov shaklini chizish. Qora rangli qogʻoz ikkiga buklanadi. Buklangan "
        "qogʻozning bir tomoniga xonqizining moʻylovi uchun egri, yoy shaklidagi "
        "kontur chiziladi. Buklama usulidan foydalanish natijasida ikki tomonlama, "
        "bir xil va simmetrik moʻylov shakli hosil qilinadi.", True),
    (10, "Moʻylovlarni qirqib olish. Buklangan qora qogʻozda chizilgan moʻylov "
         "konturi boʻylab qaychi bilan ehtiyotkorlik bilan qirqiladi. Qogʻoz "
         "ochilganda oʻlchami va shakli bir xil boʻlgan ikkita simmetrik moʻylov "
         "hosil qilinadi.", True),
    (11, "Moʻylovlarni xonqiziga biriktirish. Tayyorlangan ikkita qora moʻylov "
         "xonqizining bosh qismiga ikki tomondan simmetrik joylashtiriladi. Ularning "
         "yoʻnalishi bir xil boʻlishiga eʼtibor berilib, yelim yordamida mustahkam "
         "biriktiriladi.", True),
    (12, "Koʻzchalarni joylashtirish va ishni yakunlash. Tayyor koʻzchalar bosh "
         "qismiga oʻzaro teng masofada va simmetrik tarzda yopishtiriladi. Barcha "
         "detallar tekshiriladi, ortiqcha yelim izlari tozalanadi va tayyor xonqizi "
         "aplikatsiyasining estetik koʻrinishi baholanadi.", True),
]

_KESH = None


def _rasm(nom):
    """`?v=` — brauzer keshini yangilash uchun (statik fayllar hashlanmaydi)."""
    return f'{RASM_YOL}{nom}?v={RASM_VERSIYA}'


def bosqichlar():
    """Shablon uchun tayyor ro'yxat (bir marta yig'ilib, keshlanadi)."""
    global _KESH
    if _KESH is not None:
        return _KESH

    chiqish = []
    for nomer, matn, videosi_bor in _XOM:
        qadam = {
            'nomer': nomer,
            'matn': matn,
            'tasvir': _rasm(f'qadam{nomer:02d}.jpg'),
            'anjom_rasm': _rasm(f'anjom{nomer:02d}.jpg'),
            'tur': 'video' if videosi_bor else 'yoq',
        }
        if videosi_bor:
            sek = _DAVOMIYLIK.get(nomer, 0)
            qadam['video'] = f'{VIDEO_YOL}v{nomer:02d}.mp4'
            qadam['poster'] = _rasm(f'poster{nomer:02d}.jpg')
            qadam['davomiylik'] = '{}:{:02d}'.format(int(sek // 60), int(round(sek % 60)))
        else:
            # 1-bosqichda lavha yo'q; katak bo'sh qolmasin deb mijozning
            # tanlovi bo'yicha SO'NGGI bosqichning tasviri — tayyor buyum —
            # qo'yiladi: o'quvchi ishning boshida natijani ko'rib turadi.
            qadam['korinish'] = _rasm(f'qadam{_XOM[-1][0]:02d}.jpg')
        chiqish.append(qadam)

    _KESH = chiqish
    return chiqish


def yetishmagan_fayllar():
    """Diskda yo'q rasm/video ro'yxati — `manage.py check` shuni ogohlantiradi.

    Videolar ham sanaladi: ular `media/` da turadi va `staticfiles/` dan farqli
    o'laroq hech qanday yig'ish bosqichidan o'tmaydi, ya'ni fayl ko'chirilmay
    qolsa sahifada jimgina ishlamaydigan pleyer qoladi.
    """
    yoq = []
    for qadam in bosqichlar():
        nomer = qadam['nomer']
        kerak = [f'qadam{nomer:02d}.jpg', f'anjom{nomer:02d}.jpg']
        if qadam['tur'] == 'video':
            kerak.append(f'poster{nomer:02d}.jpg')
        yoq += [nom for nom in kerak if not (RASM_KATALOG / nom).exists()]
        if qadam['tur'] == 'video' and not (VIDEO_KATALOG / f'v{nomer:02d}.mp4').exists():
            yoq.append(f'media/…/v{nomer:02d}.mp4')
    return yoq


def video_soni():
    return sum(1 for q in bosqichlar() if q['tur'] == 'video')
