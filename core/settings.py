"""
Django sozlamalari — «Inkorporatsion amaliy topshiriqlar» metodik e-platformasi.

Sozlamalar ikki manbadan o'qiladi:
  1. Muhit o'zgaruvchilari (environment variables);
  2. Loyiha ildizidagi `.env` fayli — domenlar, HTTPS va boshqalar.

`.env` git'da turadi va serverga `git pull` bilan o'zi boradi; ichida sir
yo'q (maxfiy kalit alohida `.secret_key` da). Bu faylni tahrirlash odatda
SHART EMAS — sozlama `.env` da o'zgartiriladi. To'liq qo'llanma: DEPLOY.md
"""

import os
import secrets
import string
from pathlib import Path

# Loyiha ichidagi yo'llar shunday quriladi: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# `.env` fayli va yordamchi o'qigichlar
# ---------------------------------------------------------------------------

def _env_yukla(fayl):
    """`.env` faylidagi `KALIT=qiymat` qatorlarini muhitga qo'yadi.

    Tashqi kutubxona (python-dotenv) qo'shmaslik uchun ataylab juda sodda:
    izohlar (`#`), bo'sh qatorlar va qiymat atrofidagi qo'shtirnoq tashlanadi.
    `setdefault` — haqiqiy muhit o'zgaruvchisi har doim `.env` dan ustun turadi.
    """
    try:
        matn = fayl.read_text(encoding='utf-8-sig')
    except OSError:
        return
    for qator in matn.splitlines():
        qator = qator.strip()
        if not qator or qator.startswith('#') or '=' not in qator:
            continue
        kalit, _, qiymat = qator.partition('=')
        os.environ.setdefault(kalit.strip(), qiymat.strip().strip('"').strip("'"))


_env_yukla(BASE_DIR / '.env')


def _bayroq(nom, standart=False):
    """Muhitdagi ha/yo'q qiymatini bool ga aylantiradi."""
    qiymat = os.environ.get(nom)
    if qiymat is None or qiymat.strip() == '':
        return standart
    return qiymat.strip().lower() in ('1', 'true', 'ha', 'yes', 'on')


def _royxat(nom, standart):
    """Vergul bilan ajratilgan ro'yxatni o'qiydi (bo'sh bo'lsa — standart)."""
    qiymat = os.environ.get(nom)
    if not qiymat:
        return list(standart)
    return [b.strip() for b in qiymat.split(',') if b.strip()]


def _maxfiy_kalit():
    """SECRET_KEY ni topadi yoki bir marta yaratib, faylga saqlaydi.

    Tartib: `DJANGO_SECRET_KEY` muhit o'zgaruvchisi → `.secret_key` fayli →
    (fayl tizimi yozishga ruxsat bermasa) vaqtinchalik tasodifiy kalit.

    Shu sababli serverda hech narsa sozlamasdan ham kalit maxfiy bo'ladi:
    birinchi ishga tushishda `.secret_key` yaratiladi (u `.gitignore` da).
    DIQQAT: kalit o'zgarganda barcha ochiq sessiyalar bekor bo'ladi —
    foydalanuvchilar bir marta qaytadan kirishi kerak. Parollarga ta'sir qilmaydi.
    """
    kalit = os.environ.get('DJANGO_SECRET_KEY')
    if kalit:
        return kalit

    fayl = BASE_DIR / '.secret_key'
    try:
        saqlangan = fayl.read_text(encoding='utf-8').strip()
        if saqlangan:
            return saqlangan
    except OSError:
        pass

    alifbo = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
    yangi = ''.join(secrets.choice(alifbo) for _ in range(64))
    try:
        fayl.write_text(yangi, encoding='utf-8')
        os.chmod(fayl, 0o600)          # Windows'da e'tiborsiz qoldiriladi
    except OSError:
        pass                            # faqat shu jarayon uchun amal qiladi
    return yangi


# ---------------------------------------------------------------------------
# Asosiy
# ---------------------------------------------------------------------------

SECRET_KEY = _maxfiy_kalit()

# DIQQAT: bu loyihada DEBUG ishlab chiqishda ham False (shablonlar keshlanadi,
# statikni WhiteNoise beradi). Yoqish uchun `.env` ga `DJANGO_DEBUG=1`.
DEBUG = _bayroq('DJANGO_DEBUG', False)

# Saytning domenlari `.env` dagi DJANGO_ALLOWED_HOSTS da — faqat o'sha yerda.
# Bu yerdagi ro'yxat `.env` umuman topilmagandagi zaxira: sayt faqat shu
# kompyuterning o'zida ochiladi, begona domen «400 Bad Request» oladi.
ALLOWED_HOSTS = _royxat('DJANGO_ALLOWED_HOSTS', ["localhost", "127.0.0.1"])

CSRF_TRUSTED_ORIGINS = _royxat('DJANGO_CSRF_TRUSTED_ORIGINS', [
    f"{sxema}://{host}"
    for host in ALLOWED_HOSTS if host not in ("localhost", "127.0.0.1")
    for sxema in ("https", "http")
])


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Custom apps
    'home',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Kirish sahifasini parol terishdan himoya qiladi — izohi home/xavfsizlik.py da.
    'home.xavfsizlik.KirishCheklovi',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # `sayt_asos` — meta teglardagi to'liq manzil (izohi home/kontekst.py da)
                'home.kontekst.sayt_manzili',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Autentifikatsiya: login shart bo'lgan sahifalar (@login_required) shu manzilga
# ?next=<sahifa> bilan yo'naltiradi; login/register keyin o'sha sahifaga qaytaradi.
LOGIN_URL = '/login'


# ---------------------------------------------------------------------------
# Ma'lumotlar bazasi
# ---------------------------------------------------------------------------
# SQLite bitta yozuvchi bilan cheklangan. WAL rejimi o'qish va yozishni bir
# vaqtda ishlashiga imkon beradi (sayt asosan o'qishga ishlaydi, test natijasi
# esa yoziladi), `busy_timeout` esa bir vaqtda kelgan yozuvni xato qaytarish
# o'rniga kutishga majbur qiladi — «database is locked» xatosi shundan chiqadi.

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.environ.get('DJANGO_DB_PATH') or BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
            'init_command': (
                "PRAGMA journal_mode=WAL;"
                "PRAGMA synchronous=NORMAL;"
                "PRAGMA busy_timeout=5000;"
            ),
            'transaction_mode': 'IMMEDIATE',
        },
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

# Sana va soat sahifada mahalliy vaqtda ko'rinsin ('O'quvchilarim'
# bo'limidagi urinishlar tarixi). Ma'lumot bazada baribir UTC da
# saqlanadi (USE_TZ = True), o'zgarayotgani faqat ko'rinishi.
TIME_ZONE = 'Asia/Tashkent'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise statik fayllarni DEBUG=False da ham siqilgan holda beradi (nginxsiz).
# Shablonlar {% static %} emas, qattiq yo'l ishlatgani uchun hash QILINMAYDI —
# faqat siqish (gzip/brotli). Shu sababli statik uchun alohida URL kerak emas.
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ---------------------------------------------------------------------------
# Xavfsizlik
# ---------------------------------------------------------------------------
# Quyidagilar `.env` da `DJANGO_HTTPS=1` bo'lgandagina yoqiladi (u yerda
# yoqilgan). Nima uchun qaysi qiymat tanlangani — `.env` ning o'zida.
#
# NEGA KODDA STANDART HOLDA O'CHIQ: bu loyihada DEBUG ishlab chiqishda ham
# False, ya'ni mahalliy `runserver` ham «production» sozlamalari bilan
# ishlaydi. `.env` da DJANGO_SSL_REDIRECT=0 bo'lgani uchun mahalliy sayt
# ochiladi; aks holda http://127.0.0.1:8000 darhol https ga yo'naltirilardi.

HTTPS_ORQALI = _bayroq('DJANGO_HTTPS', False)

# Cookie'lar har doim JavaScript'ga berilmasin va boshqa saytdan yuborilmasin.
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'

if HTTPS_ORQALI:
    # TLS'ni oldindagi server (nginx / Cloudflare) tugatadi, Django'ga so'rov
    # HTTP bo'lib keladi. Django ulanish himoyalanganini shu sarlavhadan biladi.
    # DIQQAT: faqat ishonchli proksi orqasida yoqing — to'g'ridan-to'g'ri ochiq
    # serverda mijoz bu sarlavhani o'zi yuborib, tekshiruvni aldashi mumkin.
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    SECURE_SSL_REDIRECT = _bayroq('DJANGO_SSL_REDIRECT', True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # HSTS: brauzer saytga faqat HTTPS orqali kirishni eslab qoladi.
    # Birinchi haftada kichik qiymat bilan sinang (masalan 3600), hammasi
    # joyida bo'lsa bir yilga ko'taring — orqaga qaytarish oson emas.
    SECURE_HSTS_SECONDS = int(os.environ.get('DJANGO_HSTS_SECONDS') or 31536000)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = _bayroq('DJANGO_HSTS_SUBDOMAINS', True)
    SECURE_HSTS_PRELOAD = _bayroq('DJANGO_HSTS_PRELOAD', False)

# Qolgan sarlavhalar Django 5 da standart holda to'g'ri:
#   SECURE_CONTENT_TYPE_NOSNIFF = True
#   SECURE_REFERRER_POLICY = 'same-origin'
#   X_FRAME_OPTIONS = 'DENY'  (media uchun core/urls.py da SAMEORIGIN)


# ---------------------------------------------------------------------------
# Jurnal (log)
# ---------------------------------------------------------------------------
# DEBUG=False bo'lgani uchun xatolar ekranda ko'rinmaydi — ular jimgina 500
# sahifasiga aylanadi. Shuning uchun ular `logs/xato.log` ga yoziladi.

LOG_JILDI = BASE_DIR / 'logs'
try:
    LOG_JILDI.mkdir(exist_ok=True)
    _log_yoziladi = True
except OSError:
    _log_yoziladi = False

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'toliq': {
            'format': '[{asctime}] {levelname} {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'konsol': {
            'class': 'logging.StreamHandler',
            'formatter': 'toliq',
        },
    },
    'root': {
        'handlers': ['konsol'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['konsol'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

if _log_yoziladi:
    LOGGING['handlers']['fayl'] = {
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': str(LOG_JILDI / 'xato.log'),
        'maxBytes': 2 * 1024 * 1024,   # 2 MB
        'backupCount': 5,
        'encoding': 'utf-8',
        'formatter': 'toliq',
        'level': 'WARNING',
    }
    LOGGING['root']['handlers'].append('fayl')
    LOGGING['loggers']['django']['handlers'].append('fayl')
