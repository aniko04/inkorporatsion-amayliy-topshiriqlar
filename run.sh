#!/usr/bin/env bash
# «Inkorporatsion amaliy topshiriqlar» — serverda o'rnatish va yangilash.
#
#     git pull && bash run.sh
#
# Tartib: image quriladi (eski konteyner shu paytda ishlab turadi) → git'dagi
# media volume'ga qo'shiladi → konteyner almashtiriladi → sayt javob berishi
# tekshiriladi. Uzilish — faqat konteyner qayta ko'tariladigan bir necha
# soniya. Qurish yiqilsa, eski konteyner tegilmay qoladi. Batafsil: DEPLOY.md
set -euo pipefail
cd "$(dirname "$0")"

NOM=inkorporatsion-amayliy-topshiriqlar-uz
IMAGE=$NOM-image
VOLUME=${VOLUME:-/docker/volume/$NOM}
PORT=${PORT:-2026}            # nginx shu portga proksi qiladi (…uz.conf)
TARMOQ=${TARMOQ:-buxdpi}

DATA=$VOLUME/data             # baza, .secret_key, zaxira/, logs/
MEDIA=$VOLUME/media
mkdir -p "$DATA" "$MEDIA"

# Eski joylashuv (bir martalik): baza volume ildizida alohida fayl bo'lib
# ulanardi. WAL rejimida uning -wal/-shm fayllari konteyner ichida qolib,
# konteyner o'chirilganda yo'qolardi — shuning uchun endi jild ulanadi.
if [ -s "$VOLUME/db.sqlite3" ] && [ ! -e "$DATA/db.sqlite3" ]; then
    echo "📦 Baza $DATA/ ga ko'chirilmoqda (bir martalik)..."
    mv "$VOLUME/db.sqlite3" "$DATA/db.sqlite3"
fi

# Baza yo'q bo'lsa to'xtaymiz: aks holda sayt bo'sh baza bilan ko'tarilib,
# 1100 foydalanuvchi va ularning natijalari «yo'qolgandek» ko'rinardi.
if [ ! -s "$DATA/db.sqlite3" ] && [ "${YANGI_BAZA:-0}" != 1 ]; then
    cat >&2 <<EOF
❌ Baza topilmadi: $DATA/db.sqlite3
   Mavjud bazani shu yerga ko'chiring (DEPLOY.md, 1-bo'lim) yoki bo'sh
   baza bilan boshlash uchun:   YANGI_BAZA=1 bash run.sh
EOF
    exit 1
fi

# git'dagi media → volume. Faqat yangi yoki git'da yangilangan fayllar
# ko'chadi; admin paneldan yuklanganlarga tegilmaydi, hech narsa o'chmaydi.
echo "🖼  Media fayllar volume bilan tenglanmoqda..."
cp -a -u media/. "$MEDIA/"

echo "🔨 Image qurilmoqda..."
docker build -t "$IMAGE" .

docker network inspect "$TARMOQ" >/dev/null 2>&1 || docker network create "$TARMOQ" >/dev/null

echo "🔁 Konteyner almashtirilmoqda..."
docker stop -t 30 "$NOM" >/dev/null 2>&1 || true
docker rm "$NOM" >/dev/null 2>&1 || true
docker run -d \
    --name "$NOM" \
    --restart unless-stopped \
    --network "$TARMOQ" \
    -p "127.0.0.1:$PORT:8000" \
    -v "$DATA":/app/data \
    -v "$MEDIA":/app/media \
    --log-opt max-size=10m --log-opt max-file=3 \
    "$IMAGE" >/dev/null

# Shu loyihaning eski (nomsiz qolgan) image'lari — boshqa loyihalarga tegmaydi.
docker image prune -f --filter "label=loyiha=inkorporatsion-amayliy-topshiriqlar" >/dev/null

echo "⏳ Sayt javob berishi kutilmoqda..."
for _ in $(seq 1 45); do
    if [ "$(docker inspect -f '{{.State.Running}}' "$NOM" 2>/dev/null)" != true ]; then
        break
    fi
    if docker exec "$NOM" python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/', timeout=3)" >/dev/null 2>&1; then
        echo "✅ Tayyor: http://127.0.0.1:$PORT  (loglar: docker logs -f $NOM)"
        exit 0
    fi
    sleep 2
done

echo "❌ Sayt ko'tarilmadi. Oxirgi loglar:" >&2
docker logs --tail 60 "$NOM" >&2
exit 1
