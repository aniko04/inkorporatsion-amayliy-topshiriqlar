from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Avg, Case, Count, F, FloatField, Max, Q, Value, When
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme, urlencode
from django.conf import settings
from collections import defaultdict
from datetime import timedelta
from functools import wraps
from .models import Result, Profile, Material
from . import rasmli_test
from . import diktant
from . import qalamdon
from . import xonqizi
import csv
import json


# ===== Rol yordamchilari =====
def is_talaba(user):
    """6–10 mashqlarni ko'rish huquqi: talaba roli yoki xodim (admin/o'qituvchi)."""
    if not user.is_authenticated:
        return False
    if user.is_staff:
        return True
    return Profile.objects.filter(user=user, role=Profile.ROLE_TALABA).exists()


def talaba_required(view_func):
    """6–10 mashq sahifalari faqat talaba uchun; aks holda Multimediya bo'limiga qaytaradi."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not is_talaba(request.user):
            return redirect('/multimediya')
        return view_func(request, *args, **kwargs)
    return _wrapped


def _safe_next(request):
    """Login/ro'yxatdan keyin qaytariladigan xavfsiz ichki URL (ochiq-redirectdan himoya)."""
    nxt = request.GET.get('next', '')
    if nxt and url_has_allowed_host_and_scheme(
        nxt, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return nxt
    return '/'


# ===== Platforma bo'limlari =====
def home(request):
    """Bosh sahifa: platforma haqida va yetti bo'lim."""
    return render(request, 'index.html', {'active': 'home'})


def haqida(request):
    """1-bo'lim — muallif va platforma haqida."""
    foto = settings.MEDIA_ROOT / 'muallif.jpg'
    # Bo'sh satr — rasm yo'q, shablon o'rniga naqsh chiqaradi. Bor bo'lsa
    # manzil `?v=<fayl vaqti>` bilan beriladi: rasm o'sha nom bilan
    # almashtirilganda brauzer eskisini ushlab qolmasin (`Material`
    # dagi `_versiyali` bilan bir xil mantiq).
    muallif_foto = (
        f'/media/muallif.jpg?v={int(foto.stat().st_mtime)}' if foto.exists() else ''
    )
    # Ilmiy rahbarning surati ham xuddi shu tartibda: `media/rahbar.jpg`.
    rahbar = settings.MEDIA_ROOT / 'rahbar.jpg'
    rahbar_foto = (
        f'/media/rahbar.jpg?v={int(rahbar.stat().st_mtime)}' if rahbar.exists() else ''
    )
    return render(request, 'haqida.html', {
        'active': 'haqida',
        'muallif_foto': muallif_foto,
        'rahbar_foto': rahbar_foto,
    })


def multimediya(request):
    """4-bo'lim — 10 ta interaktiv topshiriq (avvalgi bosh sahifa)."""
    return render(request, 'multimediya.html', {
        'active': 'multimediya',
        'show_advanced': is_talaba(request.user),
    })


def _bolim(request, section, nomi, lede, sarlavha, guruhlash=None, ilova=None,
           bolim_ilova=None):
    """Admin orqali to'ldiriladigan material bo'limlarining umumiy ko'rinishi.

    `guruhlash` berilsa (masalan Topshiriq bo'limida), materiallar kichik
    bo'limlarga ajratiladi va sahifada har biri ochiladigan ro'yxat bo'lib
    chiqadi. Kichik bo'limi belgilanmagan materiallar guruhlardan tashqarida,
    ro'yxat boshida oddiy karta bo'lib qoladi.

    `ilova` — kichik bo'lim kaliti bo'yicha interaktiv sahifaga havola
    (masalan «Rasmli test» guruhidagi onlayn test): {kalit: {...}}.

    `bolim_ilova` — o'sha havolaning guruhsiz varianti: bo'limning eng
    boshida turadi (Xarita bo'limidagi xaritalar shunday). Xarita guruhlarga
    bo'linmagani uchun `ilova` dagi kalit tizimi bu yerda ish bermaydi.
    Bu — RO'YXAT: bo'limda bir nechta interaktiv sahifa bo'lishi mumkin
    (hozir Qalamdon va Xonqizi).
    """
    hammasi = list(Material.objects.filter(section=section, is_published=True))
    guruhlar = []
    guruhsiz = hammasi
    if guruhlash:
        kalitlar = [kalit for kalit, _ in guruhlash]
        guruhlar = [
            {
                'kalit': kalit,
                'nomi': guruh_nomi,
                'materiallar': [m for m in hammasi if m.kichik_bolim == kalit],
                'ilova': (ilova or {}).get(kalit),
            }
            for kalit, guruh_nomi in guruhlash
        ]
        guruhsiz = [m for m in hammasi if m.kichik_bolim not in kalitlar]

    return render(request, 'bolim.html', {
        'active': section,
        'bolim_nomi': nomi,
        'bolim_lede': lede,
        'bolim_sarlavha': sarlavha,
        'materiallar': guruhsiz,
        'guruhlar': guruhlar,
        'bolim_ilova': bolim_ilova,
        'jami': len(hammasi),
    })


def metodika(request):
    """2-bo'lim — metodik tavsiyalar."""
    return _bolim(
        request, Material.SECTION_METODIKA, "Metodika",
        "Inkorporatsion yondashuv, fanlararo integratsiya va interfaol metodlar bo'yicha "
        "metodik tavsiyalar hamda zamonaviy pedagogik yondashuvlar.",
        "Metodik tavsiyalar",
    )


def maqola(request):
    """3-bo'lim — ilmiy maqolalar."""
    return _bolim(
        request, Material.SECTION_MAQOLA, "Maqola",
        "Tadqiqot doirasida chop etilgan ilmiy va ilmiy-metodik maqolalar, "
        "konferensiya tezislari va nashrlar.",
        "Nashr etilgan maqolalar",
    )


def topshiriq(request):
    """5-bo'lim — amaliy topshiriqlar; ikki kichik bo'limga ajratilgan."""
    return _bolim(
        request, Material.SECTION_TOPSHIRIQ, "Topshiriq",
        "Sinfda va uyda bajarish uchun amaliy topshiriqlar to'plami hamda "
        "ularni baholash mezonlari.",
        "Amaliy topshiriqlar",
        guruhlash=Material.KICHIK_BOLIM_CHOICES,
        ilova={
            Material.KICHIK_RASMLI_TEST: {
                'url': '/topshiriq/rasmli-test',
                'sarlavha': "Onlayn rasmli test",
                'tavsif': "2–4-sinf o'quvchilari uchun {} ta topshiriq, {} ball, "
                          "{} daqiqa. Javoblar shu yerda tekshiriladi.".format(
                              len(rasmli_test.savollar()), rasmli_test.jami_ball(),
                              rasmli_test.DAQIQA),
                'tugma': "Testni boshlash",
            },
            Material.KICHIK_DIKTANT: {
                'url': '/topshiriq/diktantlar',
                'sarlavha': "Onlayn texnologik diktant",
                'tavsif': "{} bosqich, har birida {} ta topshiriq va {} daqiqa. "
                          "Bosqichlar ketma-ket ochiladi.".format(
                              diktant.BOSQICH_SONI,
                              len(diktant.bosqichlar()[0]['savollar']),
                              diktant.BOSQICH_DAQIQA),
                'tugma': "Diktantni boshlash",
            },
        },
    )


def rasmli_test_sahifa(request):
    """Topshiriq bo'limining «Rasmli test» kichik bo'limi — interaktiv test.

    Savollar va javob kaliti `home/rasmli_test.py` da; sahifa o'sha ma'lumotdan
    yig'iladi, tekshirish esa brauzerda bo'ladi (natija login qilganlarda
    `/api/save-result` orqali saqlanadi).
    """
    return render(request, 'rasmli_test.html', {
        'active': 'topshiriq',
        'savollar': rasmli_test.savollar(),
        # json_script shablonda o'zi JSON qiladi — bu yerda lug'atning o'zi beriladi.
        'javoblar': rasmli_test.javob_kaliti(),
        'jami_ball': rasmli_test.jami_ball(),
        'jami_qator': rasmli_test.jami_qator(),
        'qator_ball': rasmli_test.QATOR_BALL,
        'daqiqa': rasmli_test.DAQIQA,
    })


def diktant_sahifa(request):
    """Topshiriq bo'limining «Texnologik diktantlar» kichik bo'limi.

    Worddagi to'rt variant — to'rt bosqich. Sahifa hammasini bir marta
    yuboradi, lekin bir vaqtda bittasi ko'rinadi: bosqich tekshirilgandan
    keyin keyingisi ochiladi (JS, sahifa yangilanmaydi). Har bosqich
    natijasi `dikt1`…`dikt4` kaliti bilan alohida saqlanadi.

    Topshiriqlar har ochilishda aralashadi (rasm raqamlari ham, nom qatorlari
    ham), shuning uchun javob kaliti AYNAN shu aralashmadan olinadi — ikkisi
    bir chaqiruvdan chiqishi shart.
    """
    tuzilma = diktant.aralashtirilgan()
    return render(request, 'diktant.html', {
        'active': 'topshiriq',
        'bosqichlar': tuzilma,
        # json_script shablonda o'zi JSON qiladi — bu yerda lug'atning o'zi beriladi.
        'javoblar': diktant.javob_kaliti(tuzilma),
        'raqamlar': diktant.RAQAMLAR,
        'qator_ball': diktant.QATOR_BALL,
        'bosqich_ball': diktant.bosqich_ball(),
        'jami_ball': diktant.jami_ball(),
        'daqiqa': diktant.BOSQICH_DAQIQA,
    })


def xarita(request):
    """6-bo'lim — instruksion texnologik xaritalar."""
    return _bolim(
        request, Material.SECTION_XARITA, "Instruksion texnologik xarita",
        "Amaliy mavzular bo'yicha bosqichma-bosqich texnologik xaritalar: "
        "ish ketma-ketligi, kerakli jihozlar va xavfsizlik qoidalari.",
        "Texnologik xaritalar",
        bolim_ilova=[
            {
                'url': '/xarita/qalamdon',
                'sarlavha': qalamdon.SARLAVHA,
                'tavsif': "{} bosqichli to'liq xarita: har bosqichning tasviri, "
                          "{} ta video lavha va kerakli ish anjomlari.".format(
                              len(qalamdon.bosqichlar()), qalamdon.video_soni()),
                'tugma': "Xaritani ochish",
            },
            {
                'url': '/xarita/xonqizi',
                'sarlavha': xonqizi.SARLAVHA,
                'tavsif': "{} bosqichli to'liq xarita: har bosqichning tasviri, "
                          "{} ta video lavha va kerakli ish anjomlari.".format(
                              len(xonqizi.bosqichlar()), xonqizi.video_soni()),
                'tugma': "Xaritani ochish",
            },
        ],
    )


def qalamdon_sahifa(request):
    """«Qalamdon "Organayzer"» — Xarita bo'limining to'liq texnologik xaritasi.

    Worddagi jadval saytda to'rt ustunli bo'lib chiqadi: uchinchi «Vidyosi»
    ustuni faqat shu yerda bor (Word fayl o'zgartirilmagan). Ma'lumot
    `home/qalamdon.py` da; sahifada JS faqat videoni bosilganda ijro etadi.
    """
    return render(request, 'qalamdon.html', {
        'active': 'xarita',
        'sarlavha': qalamdon.SARLAVHA,
        # Qisqa nom — yo'l ko'rsatkichi va brauzer yorlig'i uchun
        # (to'liq sarlavha ikkalasiga ham uzun).
        'qisqa': qalamdon.QISQA,
        'tavsif': qalamdon.TAVSIF,
        'xulosa': qalamdon.XULOSA,
        'ustunlar': qalamdon.USTUNLAR,
        'bosqichlar': qalamdon.bosqichlar(),
        'video_soni': qalamdon.video_soni(),
    })


def xonqizi_sahifa(request):
    """«Applikatsiya "Xonqizi"» — Xarita bo'limining ikkinchi to'liq xaritasi.

    Tuzilishi `qalamdon_sahifa` bilan bir xil; ma'lumot `home/xonqizi.py` da.
    Farqi: 1-bosqichda video yo'q (mijozning ko'rsatmasi), qolgan 11 bosqichga
    lavhalar ketma-ket qo'yilgan.
    """
    return render(request, 'xonqizi.html', {
        'active': 'xarita',
        'sarlavha': xonqizi.SARLAVHA,
        # Qisqa nom — yo'l ko'rsatkichi va brauzer yorlig'i uchun
        # (to'liq sarlavha ikkalasiga ham uzun).
        'qisqa': xonqizi.QISQA,
        'tavsif': xonqizi.TAVSIF,
        'xulosa': xonqizi.XULOSA,
        'ustunlar': xonqizi.USTUNLAR,
        'bosqichlar': xonqizi.bosqichlar(),
        'video_soni': xonqizi.video_soni(),
    })


def ishlanma(request):
    """7-bo'lim — namunaviy dars ishlanmalari."""
    return _bolim(
        request, Material.SECTION_ISHLANMA, "Dars ishlanmalar",
        "Namunaviy dars ishlanmalari: dars maqsadi, kerakli jihozlar, dars bosqichlari "
        "va kutilayotgan natijalar.",
        "Namunaviy dars ishlanmalari",
    )


def login_view(request):
    """Login sahifasi."""
    if request.user.is_authenticated:
        return redirect(_safe_next(request))
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(_safe_next(request))
        else:
            return render(request, 'login.html', {'error': "Login yoki parol noto'g'ri!"})
    return render(request, 'login.html')


def register_view(request):
    """Ro'yxatdan o'tish sahifasi."""
    if request.user.is_authenticated:
        return redirect(_safe_next(request))
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        role = request.POST.get('role', Profile.ROLE_OQUVCHI)
        if role not in (Profile.ROLE_OQUVCHI, Profile.ROLE_TALABA):
            role = Profile.ROLE_OQUVCHI

        if not username or not password:
            return render(request, 'register.html', {'error': "Barcha maydonlarni to'ldiring!", 'role': role})
        if password != password2:
            return render(request, 'register.html', {'error': "Parollar mos kelmadi!", 'role': role})
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': "Bu login allaqachon mavjud!", 'role': role})

        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        Profile.objects.create(user=user, role=role)
        login(request, user)
        return redirect(_safe_next(request))
    return render(request, 'register.html')


def logout_view(request):
    """Chiqish."""
    logout(request)
    return redirect('/')


@require_POST
@login_required
def save_result(request):
    """Natijalarni saqlash API."""
    try:
        data = json.loads(request.body)
        mashq = data.get('mashq', '')
        score = int(data.get('score', 0))
        total = int(data.get('total', 0))

        Result.objects.create(
            user=request.user,
            mashq=mashq,
            score=score,
            total=total,
        )
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


# ===== 1–5 mashqlar (barcha rollar uchun; login shart) =====
@login_required
def mashq1(request):
    return render(request, 'mashq1.html')

@login_required
def mashq2(request):
    return render(request, 'mashq2.html')

@login_required
def mashq3(request):
    return render(request, 'mashq3.html')

@login_required
def mashq4(request):
    return render(request, 'mashq4.html')

@login_required
def mashq5(request):
    return render(request, 'mashq5.html')


# ===== O'quvchi uchun 6-mashq (talaba formati bilan bir xil; login shart) =====
@login_required
def oquvchi_m6a(request):
    return render(request, 'oquvchi/m6a.html')

@login_required
def oquvchi_m6b(request):
    return render(request, 'oquvchi/m6b.html')

@login_required
def oquvchi_m6c(request):
    return render(request, 'oquvchi/m6c.html')


# ===== O'quvchi uchun 7-mashq (Origami) =====
@login_required
def oquvchi_m7a(request):
    return render(request, 'oquvchi/m7a.html')

@login_required
def oquvchi_m7b(request):
    return render(request, 'oquvchi/m7b.html')

@login_required
def oquvchi_m7c(request):
    return render(request, 'oquvchi/m7c.html')


# ===== O'quvchi uchun 8-mashq (Fetr) — to'liq =====
@login_required
def oquvchi_m8a(request):
    return render(request, 'oquvchi/m8a.html')

@login_required
def oquvchi_m8b(request):
    return render(request, 'oquvchi/m8b.html')

@login_required
def oquvchi_m8c(request):
    return render(request, 'oquvchi/m8c.html')


# ===== O'quvchi uchun 9-mashq (Kvilling) — to'liq =====
@login_required
def oquvchi_m9a(request):
    return render(request, 'oquvchi/m9a.html')

@login_required
def oquvchi_m9a2(request):
    return render(request, 'oquvchi/m9a2.html')

@login_required
def oquvchi_m9b(request):
    return render(request, 'oquvchi/m9b.html')

@login_required
def oquvchi_m9c(request):
    return render(request, 'oquvchi/m9c.html')


# ===== O'quvchi uchun 10-mashq (Loy/plastilin) — to'liq =====
@login_required
def oquvchi_m10a(request):
    return render(request, 'oquvchi/m10a.html')

@login_required
def oquvchi_m10b(request):
    return render(request, 'oquvchi/m10b.html')

@login_required
def oquvchi_m10c(request):
    return render(request, 'oquvchi/m10c.html')


# ===== 6–10 mashqlar (faqat talaba; login ham shart) =====
@login_required
@talaba_required
def mashq6a(request):
    return render(request, 'mashq6a.html')

@login_required
@talaba_required
def mashq6b(request):
    return render(request, 'mashq6b.html')

@login_required
@talaba_required
def mashq6c(request):
    return render(request, 'mashq6c.html')

@login_required
@talaba_required
def mashq7a(request):
    return render(request, 'mashq7a.html')

@login_required
@talaba_required
def mashq7b(request):
    return render(request, 'mashq7b.html')

@login_required
@talaba_required
def mashq7c(request):
    return render(request, 'mashq7c.html')

@login_required
@talaba_required
def mashq8a(request):
    return render(request, 'mashq8a.html')

@login_required
@talaba_required
def mashq8b(request):
    return render(request, 'mashq8b.html')

@login_required
@talaba_required
def mashq8c(request):
    return render(request, 'mashq8c.html')

@login_required
@talaba_required
def mashq9a(request):
    return render(request, 'mashq9a.html')

@login_required
@talaba_required
def mashq9a2(request):
    return render(request, 'mashq9a2.html')

@login_required
@talaba_required
def mashq9b(request):
    return render(request, 'mashq9b.html')

@login_required
@talaba_required
def mashq9c(request):
    return render(request, 'mashq9c.html')

@login_required
@talaba_required
def mashq10a(request):
    return render(request, 'mashq10a.html')

@login_required
@talaba_required
def mashq10b(request):
    return render(request, 'mashq10b.html')

@login_required
@talaba_required
def mashq10c(request):
    return render(request, 'mashq10c.html')


# =========================================================
# «O'quvchilarim» — administrator uchun foydalanuvchilar va natijalar
# =========================================================
# Sahifa faqat xodim (is_staff) uchun ochiq: mijoz aynan admin profilidan
# kirganda ko'rinishini so'ragan. Rol emas, `is_staff` tekshiriladi —
# o'qituvchi (talaba) roli har kimga tegishi mumkin, u esa butun saytdagi
# 1100 dan ortiq foydalanuvchining shaxsiy natijasini ko'rmasligi kerak.

# Mashq kaliti → nishondagi qisqa yorliq. To'liq nom `Result.MASHQ_CHOICES`
# da; bu yerda faqat jadvalga sig'adigan qisqartma.
MASHQ_QISQA = {
    'm1': 'M1', 'm2': 'M2', 'm3': 'M3', 'm4': 'M4', 'm5': 'M5',
    'm6b': 'M6', 'm7b': 'M7', 'm8b': 'M8', 'm9b': 'M9', 'm10b': 'M10',
    'rtest': 'RT', 'dikt1': 'D1', 'dikt2': 'D2', 'dikt3': 'D3', 'dikt4': 'D4',
}

# Ro'yxatni saralash usullari: kalit → (yorliq, order_by argumentlari).
SARALASH = {
    'yangi':   ("Yangi ro'yxatdan o'tganlar", ['-date_joined', '-id']),
    'eski':    ("Avval ro'yxatdan o'tganlar", ['date_joined', 'id']),
    'ism':     ("Ism bo'yicha (A–Z)", ['first_name', 'last_name', 'username']),
    'faol':    ("Oxirgi faollik bo'yicha", ['-oxirgi', '-id']),
    'urinish': ("Ko'p urinish qilganlar", ['-urinish', '-id']),
    'ball':    ("Yuqori o'rtacha ball", ['-ortacha', '-id']),
}

SAHIFADA = 20          # bir sahifadagi foydalanuvchi soni
NISHON_LIMITI = 6      # jadval katagida ko'rsatiladigan natija nishoni


def admin_required(view_func):
    """Faqat xodim (administrator) uchun.

    Kirmagan bo'lsa `LOGIN_URL` ga `?next=` bilan, kirgan-u xodim bo'lmasa
    bosh sahifaga qaytaradi — `talaba_required` dagi bilan bir xil mantiq
    (sababini aytmaydi: sahifa borligini bilish ham shart emas).
    """
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            qism = urlencode({'next': request.get_full_path()})
            return redirect(f'{settings.LOGIN_URL}?{qism}')
        if not request.user.is_staff:
            return redirect('/')
        return view_func(request, *args, **kwargs)
    return _wrapped


def _foiz_ifodasi(prefiks=''):
    """`score/total` ni foizga aylantiruvchi SQL ifodasi.

    `total = 0` bo'lgan yozuvlar nolga bo'linishni keltirib chiqarmasin
    (eski yoki nuqsonli yozuvlar bo'lishi mumkin), shuning uchun `Case`.
    `prefiks` — bog'lanish yo'li: `User` dan hisoblaganda `'result__'`.

    Standart qiymat 0 EMAS, NULL: `Avg` NULL larni umuman hisobga olmaydi.
    0 bo'lganda natijasi yo'q foydalanuvchi ham «0%» bo'lib chiqardi —
    LEFT JOIN unga bitta bo'sh qator beradi, `Case` esa 0 qaytarardi.
    NULL bilan esa o'rtacha ham NULL bo'ladi va sahifada «—» ko'rinadi.
    """
    return Case(
        When(**{f'{prefiks}total__gt': 0},
             then=F(f'{prefiks}score') * 100.0 / F(f'{prefiks}total')),
        default=Value(None),
        output_field=FloatField(),
    )


def _rol(u):
    """Foydalanuvchining ko'rsatiladigan roli: (kalit, nom).

    Xodim har doim «Administrator» bo'lib chiqadi — uning ham `Profile` i
    bo'lishi mumkin, lekin ro'yxatda uni rolidan emas, huquqidan tanish
    qulayroq. Profilsiz eski hisoblar o'quvchi deb qaraladi (`is_talaba`
    ham shunday ishlaydi).
    """
    if u.is_staff:
        return 'admin', 'Administrator'
    # Profil yo'q bo'lsa RelatedObjectDoesNotExist ko'tariladi, u esa
    # AttributeError dan meros oladi — shuning uchun getattr None qaytaradi.
    profil = getattr(u, 'profile', None)
    if profil and profil.role == Profile.ROLE_TALABA:
        return 'talaba', "O'qituvchi"
    return 'oquvchi', "O'quvchi"


def _saralangan_royxat(request):
    """Filtr va saralash qo'llangan foydalanuvchilar to'plami + tanlangan sozlamalar.

    Ro'yxat ham HTML sahifada, ham CSV eksportida bir xil bo'lishi kerak,
    shuning uchun ikkala view shu bitta joydan foydalanadi.
    """
    q = request.GET.get('q', '').strip()
    rol = request.GET.get('rol', '')
    mashq = request.GET.get('mashq', '')
    holat = request.GET.get('holat', '')
    saralash = request.GET.get('saralash', 'yangi')
    if saralash not in SARALASH:
        saralash = 'yangi'

    qs = (
        User.objects
        .select_related('profile')
        .annotate(
            urinish=Count('result', distinct=True),
            otgan=Count('result', filter=Q(result__is_passed=True), distinct=True),
            ortacha=Avg(_foiz_ifodasi('result__')),
            oxirgi=Max('result__created_at'),
        )
    )

    if q:
        qs = qs.filter(
            Q(first_name__icontains=q) | Q(last_name__icontains=q)
            | Q(username__icontains=q)
        )

    if rol == 'admin':
        qs = qs.filter(is_staff=True)
    elif rol == Profile.ROLE_TALABA:
        qs = qs.filter(profile__role=Profile.ROLE_TALABA, is_staff=False)
    elif rol == Profile.ROLE_OQUVCHI:
        # Profili yo'q eski hisoblar ham o'quvchi hisoblanadi.
        qs = qs.filter(
            Q(profile__role=Profile.ROLE_OQUVCHI) | Q(profile__isnull=True),
            is_staff=False,
        )

    if mashq in MASHQ_QISQA:
        # DIQQAT: bu yerda `qs.filter(result__mashq=...)` ishlatilmaydi —
        # u yuqoridagi annotate bilan bir xil JOIN ga tushib, urinish va
        # o'rtacha hisobini FAQAT shu mashq bo'yicha qilib qo'yardi. Ichki
        # so'rov esa ro'yxatni filtrlaydi, hisoblarga tegmaydi.
        qs = qs.filter(id__in=Result.objects.filter(mashq=mashq).values('user_id'))

    if holat == 'faol':
        qs = qs.filter(urinish__gt=0)
    elif holat == 'nofaol':
        qs = qs.filter(urinish=0)

    qs = qs.order_by(*SARALASH[saralash][1])

    return qs, {
        'q': q, 'rol': rol, 'mashq': mashq, 'holat': holat, 'saralash': saralash,
    }


def _umumiy_statistika():
    """Sahifa tepasidagi kartalar uchun raqamlar."""
    jami = User.objects.count()
    admin = User.objects.filter(is_staff=True).count()
    oqituvchi = (Profile.objects
                 .filter(role=Profile.ROLE_TALABA, user__is_staff=False)
                 .count())
    ortacha = Result.objects.aggregate(x=Avg(_foiz_ifodasi()))['x'] or 0
    hafta = timezone.now() - timedelta(days=7)
    return {
        'jami': jami,
        'oquvchi': jami - oqituvchi - admin,
        'oqituvchi': oqituvchi,
        'admin': admin,
        'natija': Result.objects.count(),
        'otgan': Result.objects.filter(is_passed=True).count(),
        'ortacha': round(ortacha),
        'faol': Result.objects.values('user_id').distinct().count(),
        'hafta': Result.objects.filter(created_at__gte=hafta).count(),
    }


def _mashq_statistikasi():
    """Har bir mashq bo'yicha: urinish, to'liq bajarish va o'rtacha ball."""
    xom = {
        r['mashq']: r
        for r in Result.objects.values('mashq').annotate(
            soni=Count('id'),
            otgan=Count('id', filter=Q(is_passed=True)),
            ortacha=Avg(_foiz_ifodasi()),
            kishi=Count('user_id', distinct=True),
        )
    }
    qator = []
    for kalit, nom in Result.MASHQ_CHOICES:
        r = xom.get(kalit)
        qator.append({
            'kalit': kalit,
            'qisqa': MASHQ_QISQA.get(kalit, kalit),
            'nomi': nom,
            'soni': r['soni'] if r else 0,
            'otgan': r['otgan'] if r else 0,
            'kishi': r['kishi'] if r else 0,
            'ortacha': round(r['ortacha']) if r and r['ortacha'] is not None else 0,
        })
    return qator


@admin_required
def oquvchilarim(request):
    """Barcha foydalanuvchilar va ularning mashq natijalari (admin sahifasi)."""
    qs, sozlama = _saralangan_royxat(request)

    sahifalovchi = Paginator(qs, SAHIFADA)
    sahifa = sahifalovchi.get_page(request.GET.get('sahifa'))
    foydalanuvchilar = list(sahifa.object_list)

    # Natijalar FAQAT shu sahifadagi 20 kishi uchun olinadi — 3000 dan ortiq
    # yozuvni har safar tortish shart emas. Bitta so'rov, keyin xotirada
    # foydalanuvchi bo'yicha guruhlanadi (N+1 so'rov bo'lmasin).
    guruh = defaultdict(list)
    if foydalanuvchilar:
        for n in (Result.objects
                  .filter(user__in=foydalanuvchilar)
                  .order_by('-created_at')):
            n.qisqa = MASHQ_QISQA.get(n.mashq, n.mashq)
            guruh[n.user_id].append(n)

    for u in foydalanuvchilar:
        royxat = guruh.get(u.id, [])
        u.rol_kalit, u.rol_nomi = _rol(u)
        u.natijalari = royxat[:NISHON_LIMITI]
        u.qolgan = max(0, len(royxat) - NISHON_LIMITI)
        u.ortacha_butun = round(u.ortacha) if u.ortacha is not None else None

    return render(request, 'oquvchilarim.html', {
        'active': 'oquvchilarim',
        'sahifa': sahifa,
        # 56 ta sahifa raqamini qatorga terib bo'lmaydi — Django o'zi
        # qisqartirib beradi (1 … 7 8 [9] 10 11 … 56). Shablonda argument
        # bilan chaqirib bo'lmagani uchun shu yerda hisoblanadi.
        'raqamlar': list(sahifalovchi.get_elided_page_range(
            sahifa.number, on_each_side=2, on_ends=1)),
        'uchnuqta': Paginator.ELLIPSIS,
        'foydalanuvchilar': foydalanuvchilar,
        'topildi': sahifalovchi.count,
        'stat': _umumiy_statistika(),
        'mashq_stat': _mashq_statistikasi(),
        'mashqlar': Result.MASHQ_CHOICES,
        'saralashlar': [(k, v[0]) for k, v in SARALASH.items()],
        'soz': sozlama,
        # Filtr bo'sh bo'lmasa sahifada «Tozalash» tugmasi chiqadi.
        'filtrlangan': any(sozlama[k] for k in ('q', 'rol', 'mashq', 'holat')),
    })


@admin_required
def oquvchi_natija(request, pk):
    """Bitta foydalanuvchining to'liq natijalar tarixi."""
    u = get_object_or_404(User.objects.select_related('profile'), pk=pk)
    natijalar = list(Result.objects.filter(user=u).order_by('-created_at'))
    for n in natijalar:
        n.qisqa = MASHQ_QISQA.get(n.mashq, n.mashq)

    # Mashqlar kesimi: har bir mashq bo'yicha eng yaxshi natija va urinishlar.
    kesim = []
    for kalit, nom in Result.MASHQ_CHOICES:
        oid = [n for n in natijalar if n.mashq == kalit]
        kesim.append({
            'kalit': kalit,
            'qisqa': MASHQ_QISQA.get(kalit, kalit),
            'nomi': nom,
            'urinish': len(oid),
            'eng': max((n.percentage for n in oid), default=None),
            'otgan': any(n.is_passed for n in oid),
            'oxirgi': oid[0].created_at if oid else None,
        })

    foizlar = [n.percentage for n in natijalar]
    rol_kalit, rol_nomi = _rol(u)
    return render(request, 'oquvchi_natija.html', {
        'active': 'oquvchilarim',
        'u': u,
        'rol_kalit': rol_kalit,
        'rol_nomi': rol_nomi,
        'natijalar': natijalar,
        'kesim': kesim,
        'urinish': len(natijalar),
        'otgan': sum(1 for n in natijalar if n.is_passed),
        'ortacha': round(sum(foizlar) / len(foizlar)) if foizlar else None,
        'bajarilgan': sum(1 for k in kesim if k['urinish']),
        'jami_mashq': len(kesim),
    })


@admin_required
def oquvchilarim_eksport(request):
    """Ro'yxatni yoki natijalarni CSV bo'lib yuklab berish.

    Filtrlar HTML sahifadagi bilan bir xil (`_saralangan_royxat`), ya'ni
    ekranda nima ko'rinsa, faylga ham o'sha tushadi.

    Excel uchun ikki nozik joy: fayl boshida BOM turishi kerak (aks holda
    o'zbekcha belgilar buziladi) va ustunlar `;` bilan ajratiladi —
    mintaqaviy sozlamada ro'yxat ajratgichi shu.
    """
    qs, _ = _saralangan_royxat(request)
    tur = request.GET.get('tur', 'royxat')

    javob = HttpResponse(content_type='text/csv; charset=utf-8')
    nom = 'natijalar' if tur == 'natija' else 'foydalanuvchilar'
    sana = timezone.localtime().strftime('%Y-%m-%d')
    javob['Content-Disposition'] = f'attachment; filename="{nom}-{sana}.csv"'
    javob.write('﻿')                    # BOM — Excel uchun
    yozuvchi = csv.writer(javob, delimiter=';')

    if tur == 'natija':
        yozuvchi.writerow([
            'Familiya', 'Ism', 'Login', 'Rol', 'Mashq', "To'g'ri", 'Jami',
            'Foiz', "To'liq bajarilgan", 'Sana',
        ])
        nomlar = dict(Result.MASHQ_CHOICES)
        for n in (Result.objects
                  .filter(user__in=qs.values('id'))
                  .select_related('user', 'user__profile')
                  .order_by('user__last_name', 'user__first_name', '-created_at')):
            yozuvchi.writerow([
                n.user.last_name, n.user.first_name, n.user.username,
                _rol(n.user)[1], nomlar.get(n.mashq, n.mashq), n.score, n.total,
                n.percentage, 'ha' if n.is_passed else "yo'q",
                timezone.localtime(n.created_at).strftime('%d.%m.%Y %H:%M'),
            ])
    else:
        yozuvchi.writerow([
            'Familiya', 'Ism', 'Login', 'Rol', "Ro'yxatdan o'tgan",
            'Urinishlar', "To'liq bajarilgan", "O'rtacha foiz", 'Oxirgi faollik',
        ])
        for u in qs:
            yozuvchi.writerow([
                u.last_name, u.first_name, u.username, _rol(u)[1],
                timezone.localtime(u.date_joined).strftime('%d.%m.%Y'),
                u.urinish, u.otgan,
                round(u.ortacha) if u.ortacha is not None else '',
                timezone.localtime(u.oxirgi).strftime('%d.%m.%Y %H:%M') if u.oxirgi else '',
            ])
    return javob
