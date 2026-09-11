# «Inkorporatsion amaliy topshiriqlar» — production image.
#
# Serverda qo'lda emas, `bash run.sh` bilan quriladi va ishga tushiriladi.
# Image ichida faqat kod va yig'ilgan statik fayllar bor. Ish vaqtida
# o'zgaradigan hamma narsa volume'larda (run.sh ulaydi):
#   /app/data   baza (+ -wal/-shm), .secret_key, zaxira/, logs/
#   /app/media  kitoblar, videolar, admin paneldan yuklangan fayllar
# Batafsil: DEPLOY.md
FROM python:3.11-slim

LABEL loyiha=inkorporatsion-amayliy-topshiriqlar

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_ROOT_USER_ACTION=ignore \
    DJANGO_SETTINGS_MODULE=core.settings \
    DJANGO_DATA_DIR=/app/data

WORKDIR /app

# Paketlar alohida qatlamda: requirements.txt o'zgarmasa, kod o'zgarganda
# qayta o'rnatilmaydi. Hammasi toza Python — kompilyator va kutubxonalar
# (libjpeg va h.k.) kerak emas.
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# 1) Statik fayllar QURISH paytida yig'iladi va siqiladi (WhiteNoise, gzip).
#    Kalit faqat shu qadam uchun — aks holda sozlamalar yangi kalitni image
#    ichiga yozib qo'yardi. Haqiqiy kalit volume'da: data/.secret_key.
# 2) Sayt root emas, `app` nomidan ishlaydi (docker-entrypoint.sh o'tkazadi).
# 3) Skript Windows'da CRLF bilan saqlangan bo'lsa ham `sh` o'qiy olsin.
RUN DJANGO_SECRET_KEY=faqat-qurish-uchun python manage.py collectstatic --noinput \
 && groupadd --gid 10001 app \
 && useradd --uid 10001 --gid app --no-create-home --home-dir /app --shell /usr/sbin/nologin app \
 && mkdir -p /app/data /app/media \
 && chown -R app:app /app/data /app/media \
 && sed -i 's/\r$//' docker-entrypoint.sh

VOLUME ["/app/data", "/app/media"]
EXPOSE 8000

# Waitress SIGINT ni ushlab, ochiq so'rovlarni tugatib chiqadi. SIGTERM esa
# PID 1 da e'tiborsiz qolardi — `docker stop` 10 soniya kutib, o'ldirardi.
STOPSIGNAL SIGINT

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/', timeout=4)"]

ENTRYPOINT ["sh", "/app/docker-entrypoint.sh"]

# Waitress — toza Python WSGI server (requirements.txt).
#   --threads=16       bir vaqtda 16 so'rov (video/PDF uzatish ham oqim egallaydi)
#   --trusted-proxy=*  nginx yuborgan X-Forwarded-* ga ishonish. Konteynerga faqat
#                      host'dagi nginx yetadi (run.sh portni 127.0.0.1 ga bog'laydi),
#                      lekin u Docker tarmog'i orqali o'zgaruvchan IP dan keladi —
#                      shuning uchun aniq IP emas, `*`.
# Bu ikki sarlavhasiz Django HTTPS ni ham, mijozning haqiqiy IP sini ham ko'rmaydi:
# HSTS yuborilmaydi, kirish cheklovi esa butun sayt uchun BITTA hisob yuritadi.
CMD ["python", "-m", "waitress", \
     "--listen=0.0.0.0:8000", \
     "--threads=16", \
     "--trusted-proxy=*", \
     "--trusted-proxy-headers=x-forwarded-proto x-forwarded-for", \
     "core.wsgi:application"]
