"""«Qalamdon "Organayzer"» — origami usulida qalamdon yasashning instruksion
texnologik xaritasi.

Manba: `malumotlar/texnologikxarita/qalamdon/Qalamdon  Organayzer.docx` —
13 bosqichli jadval. Worddagi jadvalda uch mazmunli ustun bor edi
(ketma-ketlik / tasviri / kerakli anjomlar); saytda ular orasiga TO'RTINCHI —
**«Vidyosi»** ustuni qo'shildi va «Kerakli ish anjomlari» oxiriga surildi.
Word faylining o'zi o'zgartirilmagan: bu ustun faqat saytda bor.

Video ustunining manbasi — o'sha papkadagi `1..13` raqamli fayllar, ya'ni
tartib raqami to'g'ridan-to'g'ri bosqich raqamiga mos. Ularning 9 tasi mp4,
3 tasi (1, 11, 12) esa surat, shuning uchun bu ustunda ikki xil katak
bo'ladi va shablon `tur` maydoniga qarab ajratadi.

13-bosqich alohida: unga keyinroq mijozning to'liq darsligi qo'shildi
(`Qog'ozdan_qalam_stendi…mp4`, 4 daqiqa, 640x360, OVOZI SAQLANGAN — qolgan
9 lavhadan farqli). Katakning yuzida turadigan `poster13.jpg` ham alohida:
u videodan olingan kadr EMAS, balki tayyor buyumning surati (manba
`13.png`, 760px) — mijoz shuni so'ragan. Bir marta videodan kadr olib
ko'rilgan edi, lekin qaytarildi; ya'ni bu poster videoni almashtirmasa
ham o'zgarmaydi.

**Videolar qayta kodlangan, va buni tushirib qoldirib bo'lmaydi:** asl
fayllar HEVC (H.265) 1080p edi — bu kodekni Chrome Windowsda faqat tizimda
alohida kengaytma bo'lsa o'ynatadi, Firefox esa umuman o'ynatmaydi, ya'ni
o'quvchining ekranida qora to'rtburchak qolardi. Shuning uchun hammasi
H.264 (yuv420p, 1280px, CRF 26, `+faststart`) ga o'girilgan va **ovoz izmi
butunlay olib tashlangan** (`-an`) — sahifada video ovozsiz turishi kerak,
`muted` atributiga ishonib qolgandan ko'ra ovozning o'zi bo'lmagani aniq.
Hajmi 49 MB dan 8.3 MB ga tushdi.

Rasmlar `static/img/qalamdon/` da: `qadamNN.jpg` — bosqich tasviri (Word
ichidan), `anjomNN.jpg` — kerakli anjomlar. Anjom rasmlarining hammasi Worddan
emas, MIJOZ bergan to'plamdan: 1–12 izohli rasmlar («Qaychi», «Tish
kovlagich» va h.k.), 13-bosqichniki esa keyinroq alohida berilgan tayyor
buyum surati (ko'k-sariq origami qalamdon; ilgari bu yerda Worddan
qolgan kvadrat rasm turardi). Yangi
rasmlarning chetida ingichka qora ramka bor edi — u kulrang soyasi bilan
birga qirqib tashlangan (skript `scratchpad/anjomlar.py` da). Ular
katak nisbatiga (1.133) oq bilan to'ldirilgan — katak `object-fit: cover`
bilan to'ladi, izoh matni esa qirqilmaydi. Rasmli test va Diktantdagi
to'rt qoida bu yerda ham amal qiladi: Worddagi JPEG bayti o'zgarishsiz
nusxalanadi, PNG shaffofligi OQQA yotqizilib q97/`subsampling=0` bilan
saqlanadi (manbalar 164–275px, tekis ranglari past sifatda buziladi),
rasm hech qachon kattalashtirilmaydi va kengaytma hammasida `.jpg`.
Bir xil anjom rasmi bir necha bosqichda takrorlanadi (masalan 3- va
8-bosqichda), lekin har bosqich uchun alohida faylga yoziladi — fayl nomi
faqat bosqich raqamiga bog'liq bo'lsin, aks holda rasmlar qayta yasalganda
manzillar siljib ketadi.

Videolar `media/` da (loyihadagi odat: `/media/Video1.mp4`), rasmlar esa
`static/` da. Video `static/` ga qo'yilmadi: WhiteNoise mp4 ni gzip qilishga
urinib, `staticfiles/` ga yana bir nusxa yozadi — bu git omboriga behuda
yuk bo'lardi.
"""

from pathlib import Path

RASM_YOL = '/static/img/qalamdon/'
VIDEO_YOL = '/media/xarita/qalamdon/'
RASM_VERSIYA = 8         # rasm o'sha nom bilan almashtirilsa oshiriladi (brauzer keshi)

RASM_KATALOG = Path(__file__).resolve().parent.parent / 'static' / 'img' / 'qalamdon'
VIDEO_KATALOG = Path(__file__).resolve().parent.parent / 'media' / 'xarita' / 'qalamdon'

# Sahifaning to'liq nomi — mijozning o'z iborasi (2026-09-05). Sarlavha
# `<h1>` da va Xarita bo'limidagi havola kartasida chiqadi.
SARLAVHA = 'Origami usulidan foydalanib «Organayzer» yasash texnologiyasi'
# Yo'l ko'rsatkichi (crumbs) va brauzer yorlig'i uchun qisqa nom: to'liq
# ibora 60 belgidan oshadi, yorliqda esa «Origami usulidan foyd…» bo'lib
# qirqiladi va yo'l ko'rsatkichini ikki qatorga bo'lib yuboradi.
QISQA = '«Organayzer»'
# Lede sarlavhani TAKRORLAMAYDI: ilgari «Origami usulida qalamdon
# «Organayzer» yasash…» deb boshlanardi, yangi sarlavha ostida esa bu
# so'zma-so'z takror bo'lib qolardi (jadval ustidagi `<caption>` ham
# aynan shu sababdan olib tashlangan edi).
TAVSIF = (
    "Ishni bajarish ketma-ketligi, har bosqichning tasviri va video lavhasi "
    "hamda kerakli ish anjomlari — bitta jadvalda."
)
XULOSA = (
    "Origami texnologiyasi asosida tayyorlangan qalamdon oʻquvchilarda ijodiy "
    "fikrlash, aniqlik, diqqat, mayda motorika hamda konstruktorlik "
    "koʻnikmalarini rivojlantiradi. Ish jarayonida qogʻozni buklash texnikasiga "
    "rioya qilish, geometrik shakllarni toʻgʻri hosil qilish va estetik bezatish "
    "malakalari shakllanadi."
)

# Ustun sarlavhalari. Wordda uchinchisi yo'q edi, to'rtinchisi esa
# «Kerakli ish anjomlari» deb yozilgan; mijoz ikkalasini ham qisqartirdi —
# jadval boshida uzun sarlavha ustunni siqib qo'yardi.
USTUNLAR = [
    "Ishni bajarish ketma-ketligi",
    "Ishni bajarish boʻyicha amalga oshiriladigan ishlar tasviri",
    "Video",
    "Anjomlar",
]

# Lavhalar davomiyligi (soniya) — katakdagi «VIDEO 0:08» yorlig'i uchun.
# Fayldan o'qilmaydi: buning uchun har sahifa ochilishida ffprobe kerak
# bo'lardi, videolar esa qayta kodlanmasa o'zgarmaydi.
_DAVOMIYLIK = {2: 8.0, 3: 5.6, 4: 2.4, 5: 7.8, 6: 3.6, 7: 2.8, 8: 7.9, 9: 7.1,
               10: 7.7, 13: 244.8}

# (bosqich, matn, video turi, anjom matni)
# Matnlar Worddan o'zgartirilmasdan olingan; faqat qo'shtirnoqsimon
# apostroflar (U+2018/U+2019) sayt bo'ylab ishlatiladigan ʻ (U+02BB) ga
# keltirilgan — diktant.py da ham shunday.
# `tur`: 'video' → mp4, 'rasm' → surat (1, 11, 12-bosqichlar).
_XOM = [
    # Wordda 1-bosqichning anjomlari matn bilan berilgan edi («Rangli qogʻoz,
    # rangli toshlar, yelim.»). Mijoz uni olib tashlashni so'radi: endi bu
    # ustunda rasm bor, matn esa katakni qo'shnilaridan baland qilib qo'yardi.
    (1, "Ish uchun A4 formatdagi rangli qogʻoz tanlab olinadi. Ish joyi tartibga "
        "keltirilib, zarur jihoz va materiallar tayyorlanadi.", 'rasm', None),
    (2, "Qogʻoz varagʻi uzunligi boʻylab teng ikkiga buklanib, buklash chizigʻi "
        "hosil qilinadi.", 'video', None),
    (3, "Hosil qilingan markaziy chiziq boʻylab qogʻoz qayta buklanib, aniq "
        "simmetrik shakl hosil qilinadi.", 'video', None),
    (4, "Qogʻoz ochilib, hosil boʻlgan buklash chiziqlari keyingi bosqichlarda "
        "yoʻriqnoma sifatida foydalanish uchun belgilab olinadi.", 'video', None),
    (5, "Belgilangan chiziqlar asosida qogʻozning yuqori qismlari ichki tomonga "
        "buklanib, dastlabki geometrik shakl hosil qilinadi.", 'video', None),
    (6, "Qarama-qarshi burchaklar oʻlchamga rioya qilingan holda markaz tomonga "
        "buklanadi va simmetrik koʻrinish hosil qilinadi.", 'video', None),
    (7, "Shaklning ikki tomoni markaziy oʻq boʻylab ichkariga buklanib, detalning "
        "konstruktiv qismi shakllantiriladi.", 'video', None),
    (8, "Qarama-qarshi tomonlar orqa qismga buklanib, biriktirish uchun maxsus "
        "choʻntakcha hosil qilinadi.", 'video', None),
    (9, "Hosil qilingan choʻntak qismlar bir-biriga kiritilib, detal mustahkam "
        "holatga keltiriladi.", 'video', None),
    (10, "Natijada qalamdonning bitta moduli tayyorlanadi va keyingi modullarni "
         "tayyorlash uchun namuna sifatida foydalaniladi.", 'video', None),
    (11, "Xuddi shu texnologik usul asosida jami olti dona bir xil modul "
         "tayyorlanadi.", 'rasm', None),
    (12, "Tayyorlangan modullar belgilangan tartibda oʻzaro biriktirilib, koʻp "
         "qirrali qalamdon konstruksiyasi hosil qilinadi.", 'rasm', None),
    # 13-bosqich mijozning to'liq darsligi (4 daqiqa) — qolgan lavhalardan
    # farqli o'laroq uzun va OVOZLI.
    (13, "Tayyor buyum bezak elementlari bilan estetik jihatdan boyitilib, "
         "foydalanishga tayyor origami qalamdoni hosil qilinadi.", 'video', None),
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
    for nomer, matn, tur, anjom_matn in _XOM:
        qadam = {
            'nomer': nomer,
            'matn': matn,
            'tasvir': _rasm(f'qadam{nomer:02d}.jpg'),
            'tur': tur,
            'anjom_matn': anjom_matn,
            'anjom_rasm': _rasm(f'anjom{nomer:02d}.jpg'),
        }
        if tur == 'video':
            sek = _DAVOMIYLIK.get(nomer, 0)
            qadam['video'] = f'{VIDEO_YOL}v{nomer:02d}.mp4'
            qadam['poster'] = _rasm(f'poster{nomer:02d}.jpg')
            qadam['davomiylik'] = '{}:{:02d}'.format(int(sek // 60), int(round(sek % 60)))
        else:
            qadam['korinish'] = _rasm(f'v{nomer:02d}.jpg')
        chiqish.append(qadam)

    _KESH = chiqish
    return chiqish


def yetishmagan_fayllar():
    """Diskda yo'q rasm/video ro'yxati — `manage.py check` shuni ogohlantiradi.

    Videolar ham tekshiriladi: ular `media/` da turadi va `staticfiles/` dan
    farqli o'laroq hech qanday yig'ish bosqichidan o'tmaydi, ya'ni fayl
    ko'chirilmay qolsa sahifada jimgina ishlamaydigan pleyer qoladi.
    """
    yoq = []
    for qadam in bosqichlar():
        nomer = qadam['nomer']
        yoq += [
            nom for nom in (f'qadam{nomer:02d}.jpg',
                            f'anjom{nomer:02d}.jpg',
                            f'poster{nomer:02d}.jpg' if qadam['tur'] == 'video' else None,
                            f'v{nomer:02d}.jpg' if qadam['tur'] == 'rasm' else None)
            if nom and not (RASM_KATALOG / nom).exists()
        ]
        if qadam['tur'] == 'video' and not (VIDEO_KATALOG / f'v{nomer:02d}.mp4').exists():
            yoq.append(f'media/…/v{nomer:02d}.mp4')
    return yoq


def video_soni():
    return sum(1 for q in bosqichlar() if q['tur'] == 'video')
