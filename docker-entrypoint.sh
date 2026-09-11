#!/bin/sh
# Konteyner ishga tushganda bajariladi (Dockerfile → ENTRYPOINT), oxirida
# CMD dagi serverga o'tadi. Batafsil: DEPLOY.md
set -e

# 1) root sifatida: volume'lar egasini to'g'rilab, `app` ga o'tish.
#    Host'dagi jildlarni root yaratadi (run.sh) — sayt esa ularga yozishi
#    kerak: baza va uning -wal/-shm fayllari, zaxira, jurnal, admin paneldan
#    yuklanadigan fayllar. Yoza olmasa har bir yozuv «readonly database»
#    xatosi bilan tushadi.
if [ "$(id -u)" = "0" ]; then
    chown -R app:app /app/data /app/media \
        || echo "[ishga tushish] OGOHLANTIRISH: volume egasini o'zgartirib bo'lmadi"
    exec setpriv --reuid=app --regid=app --init-groups sh "$0" "$@"
fi

# 2) Baza sxemasi. Yangi migratsiya bo'lsa — undan OLDIN zaxira nusxa:
#    migratsiya bazani o'zgartiradi, orqaga qaytish esa faqat nusxadan.
if ! python manage.py migrate --check >/dev/null 2>&1; then
    echo "[ishga tushish] yangi migratsiya bor — avval baza zaxirasi olinadi"
    python manage.py zaxira || echo "[ishga tushish] zaxira olinmadi (baza hali bo'shmi?)"
fi
python manage.py migrate --noinput

exec "$@"
