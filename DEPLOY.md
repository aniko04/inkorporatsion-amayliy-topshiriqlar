# Serverga o'rnatish va yangilash

«Inkorporatsion amaliy topshiriqlar» metodik e-platformasi — Django 5.2 (LTS),
SQLite, WhiteNoise. Serverda **Docker** konteynerida ishlaydi, oldida host'dagi
nginx turadi (HTTPS). Kundalik yangilash — bitta buyruq:

```bash
cd /github/inkorporatsion-amayliy-topshiriqlar
git pull && bash run.sh
```

---

## Tuzilish

| Fayl | Vazifasi |
|---|---|
| `Dockerfile` | image: Python 3.11, paketlar, kod; statik fayllar shu yerda yig'iladi |
| `docker-entrypoint.sh` | konteyner ishga tushganda: volume egasi → `app` foydalanuvchisi → migratsiya (oldidan zaxira) → server |
| `run.sh` | serverda: image qurish, media'ni volume'ga qo'shish, konteynerni almashtirish, tekshirish |
| `inkorporatsion-amayliy-topshiriqlar.uz.conf` | nginx: `127.0.0.1:2026` ga proksi |
| `.env` | domenlar va HTTPS sozlamalari — git'da, image ichiga o'zi kiradi |

Ish vaqtida o'zgaradigan hamma narsa host'dagi bitta jildda turadi — image
o'chirilib qayta qurilsa ham joyida qoladi:

```
/docker/volume/inkorporatsion-amayliy-topshiriqlar-uz/
├── data/    → /app/data    db.sqlite3 (+ -wal, -shm), .secret_key, zaxira/, logs/
└── media/   → /app/media   kitoblar, videolar, admin paneldan yuklangan fayllar
```

**Saytning eng qimmat qismi — shu jild.** Kod git'da, bu yerdagilar esa yo'q.

Konteyner ichida sayt root emas, `app` (uid 10001) nomidan ishlaydi. Server —
waitress, 16 oqim, konteynerning 8000-porti; host'da u faqat `127.0.0.1:2026`
da ochiq, ya'ni tashqaridan faqat nginx orqali kiriladi.

---

## ⚠️ Baza git'da yo'q

`db.sqlite3` git'ga kirmaydi — ichida parol hash'lari va 1100 dan ortiq
foydalanuvchining shaxsiy ma'lumoti bor. U faqat volume'da yashaydi:
`data/db.sqlite3`. Mahalliy kompyuterda admin panel orqali qo'shilgan material
serverga o'zi bormaydi (va aksincha) — bazani qo'lda ko'chirish kerak.

`run.sh` baza topilmasa **ishga tushmaydi**: aks holda sayt bo'sh baza bilan
ko'tarilib, barcha foydalanuvchilar «yo'qolgandek» ko'rinardi. Ataylab bo'sh
baza bilan boshlash kerak bo'lsa: `YANGI_BAZA=1 bash run.sh`.

---

## 1. Birinchi o'rnatish

Serverda kerak: Docker, nginx, certbot, git.

**1) Kod**

```bash
git clone <repo> /github/inkorporatsion-amayliy-topshiriqlar
cd /github/inkorporatsion-amayliy-topshiriqlar
```

**2) Baza va kalit — volume'ga**

```bash
V=/docker/volume/inkorporatsion-amayliy-topshiriqlar-uz
sudo mkdir -p $V/data
```

Baza qayerdaligiga qarab:

- **Eski (Docker'siz) o'rnatishdan.** Avval eski saytni to'xtating
  (`sudo systemctl stop beshbarmoq`) — shunda WAL'dagi oxirgi yozuvlar asosiy
  faylga tushadi. Keyin bazani va kalitni ko'chiring:
  ```bash
  sudo cp /eski/loyiha/db.sqlite3 /eski/loyiha/.secret_key $V/data/
  sudo systemctl disable beshbarmoq     # ikkinchi nusxa ishlab qolmasin
  ```
- **Boshqa kompyuterdan.** U yerda `python manage.py zaxira` bilan nusxa oling
  va uni `$V/data/db.sqlite3` nomi bilan qo'ying (`scp`).
- **Oldingi `run.sh` bazani `$V/db.sqlite3` ga qo'ygan bo'lsa** — hech narsa
  qilmang, yangi `run.sh` uni `data/` ga o'zi ko'chiradi.

`.secret_key` ko'chirilmasa yangisi yaratiladi: hamma bir marta qaytadan
kiradi, parollarga ta'sir qilmaydi.

**3) nginx va sertifikat** — buyruqlar `inkorporatsion-amayliy-topshiriqlar.uz.conf`
faylining boshida yozilgan. `www` ham shu serverga ishora qiladi, sertifikat
ikkalasiga birga olinadi.

**4) Ishga tushirish**

```bash
bash run.sh
```

---

## 2. Yangilash

```bash
git pull && bash run.sh
```

`run.sh` nima qiladi:

1. Yangi image quradi — eski konteyner shu paytda ishlab turadi. Qurish
   yiqilsa, sayt tegilmay qoladi.
2. git'dagi yangi va yangilangan media fayllarni volume'ga qo'shadi. Admin
   paneldan yuklanganlarga tegmaydi, hech narsani o'chirmaydi.
3. Konteynerni almashtiradi — uzilish bir necha soniya.
4. Konteyner ishga tushishda yangi migratsiya bo'lsa, **avval baza zaxirasini**
   oladi, keyin migratsiyani bajaradi.
5. Sayt javob berguncha kutadi; ko'tarilmasa oxirgi loglarni ko'rsatib, xato
   bilan chiqadi.

Har qanday o'zgarish (shablon, CSS, `.env`) uchun shu bitta buyruq. Shablon
keshi, WhiteNoise indeksi, eski statik — hammasi yangi konteyner bilan
yangilanadi, alohida restart kerak emas.

`git pull` «local changes would be overwritten» deb to'xtasa, serverda fayl
qo'lda o'zgartirilgan (ko'pincha `.env`): `git checkout -- .env` va qayta pull.

---

## 3. `.env` — sozlamalar

Domenlar, HTTPS va HSTS — **bitta `.env` faylida**. U git'da turadi va image
ichiga o'zi kiradi: kompyuterda o'zgartirib push qilasiz, serverda
`git pull && bash run.sh`. Har bir qator nima uchun shunday ekani faylning
o'zida yozilgan.

- **Serverda qo'lda tahrirlamang** — keyingi `git pull` to'xtab qoladi.
- **Yangi domen** — `DJANGO_ALLOWED_HOSTS` qatoriga (CSRF ro'yxati undan o'zi
  yasaladi) va nginx'dagi `server_name` ga.
- Ichida sir yo'q. Yagona sir — maxfiy kalit — volume'da: `data/.secret_key`.
  Sayt birinchi ishga tushganda uni o'zi yaratadi. **O'chirmang**: yangi kalit
  bilan hamma bir marta chiqib ketadi.

Hozirgi holat: HTTPS yoqilgan (`DJANGO_HTTPS=1`), `http → https` ni nginx qiladi
(`DJANGO_SSL_REDIRECT=0` — ikkalasi birga cheksiz yo'naltirish halqasiga olib
kelishi mumkin), HSTS hozircha 1 soat va poddomenlarsiz.

---

## 4. Statik va media — WhiteNoise

Ikkalasini ham sayt o'zi beradi, nginx faqat proksi.

- **Statik** (`/static/`) — image qurilganda `collectstatic` bilan yig'iladi va
  gzip'lanadi. `staticfiles/` git'da saqlanmaydi.
- **Media** (`/media/`) — `home/statik.py`. WhiteNoise faylni har so'rovda
  diskdan topadi va beradi:
  - `Range` (206) — videoni o'rtasiga o'tkazish ishlaydi, Safari/iOS da ijro
    etiladi (oldingi Django `serve()` buni bilmasdi);
  - `ETag` / `304` va `Cache-Control` — brauzer faylni qayta yuklamaydi;
  - `X-Frame-Options: SAMEORIGIN` — PDF ko'ruvchi o'z saytimizda ochiladi,
    begona saytda yo'q;
  - admin paneldan yuklangan fayl **darhol** ochiladi, qayta ishga tushirish
    shart emas;
  - `/media/../…` kabi urinishlar — 404.
- Media'ning asl joyi — volume. git'dagi `media/` jildini `run.sh` har safar
  unga qo'shib boradi.

---

## 5. Zaxira nusxa

Avtomatik, hech narsa qilish shart emas: sayt ishga tushganda (oxirgi nusxa
24 soatdan eski bo'lsa) va har yangi migratsiyadan oldin. Nusxalar
`data/zaxira/` da, oxirgi **14 tasi** saqlanadi.

Qo'lda:

```bash
docker exec inkorporatsion-amayliy-topshiriqlar-uz python manage.py zaxira
docker exec inkorporatsion-amayliy-topshiriqlar-uz python manage.py zaxira --royxat
```

Nusxa SQLite'ning o'z `.backup` amali bilan olinadi — sayt ishlab turganda ham
butun chiqadi. **Ishlab turgan bazani `cp` bilan nusxalamang**: oxirgi yozuvlar
`db.sqlite3-wal` da bo'lishi mumkin.

Nusxadan tiklash:

```bash
docker stop inkorporatsion-amayliy-topshiriqlar-uz
cd /docker/volume/inkorporatsion-amayliy-topshiriqlar-uz/data
rm -f db.sqlite3-wal db.sqlite3-shm          # eski bazaning WAL'i yangisiga tushmasin
cp zaxira/db_2026-09-11_140905.sqlite3 db.sqlite3
docker start inkorporatsion-amayliy-topshiriqlar-uz
```

**Nusxalar ham shu serverda turibdi.** Vaqti-vaqti bilan `data/zaxira/` va
`media/` ni boshqa joyga ko'chiring:

```bash
tar czf ~/inko_$(date +%F).tar.gz -C /docker/volume/inkorporatsion-amayliy-topshiriqlar-uz data/zaxira media
```

---

## 6. Tekshiruv va xavfsizlik

```bash
docker ps --filter name=inkorporatsion-amayliy-topshiriqlar-uz     # STATUS: Up … (healthy)
docker logs -f inkorporatsion-amayliy-topshiriqlar-uz
docker exec inkorporatsion-amayliy-topshiriqlar-uz python manage.py check --deploy
```

`check --deploy` uchta ogohlantirish beradi — uchalasi ham `.env` da ataylab:
`W005` (HSTS poddomenlarga emas), `W008` (https'ga nginx yo'naltiradi), `W021`
(preload yo'q). Boshqasi chiqsa, `.env` o'qilmayapti.

Nima himoyalangan:

- sayt konteynerda root emas, `app` nomidan ishlaydi; port faqat `127.0.0.1` da;
- baza va `.secret_key` image ichida yo'q va web orqali ochilmaydi;
- parol terish cheklangan (`home/xavfsizlik.py`): `/admin/` ga 10 ta xato
  urinishdan keyin IP 15 daqiqaga, oddiy kirishga 30 tadan keyin 10 daqiqaga
  bloklanadi. Buning uchun waitress nginx yuborgan `X-Forwarded-For` ga
  ishonadi (`Dockerfile`, `--trusted-proxy`) — usiz hamma bitta IP bo'lib
  ko'rinardi;
- HSTS, `Secure` + `HttpOnly` + `SameSite=Lax` cookie'lar, `X-Frame-Options: DENY`
  (media uchun `SAMEORIGIN`), `X-Content-Type-Options: nosniff`.

---

## 7. Xatolarni topish

Loglar: `docker logs inkorporatsion-amayliy-topshiriqlar-uz` va
`data/logs/xato.log` (2 MB dan oshsa aylanadi, 5 ta eski nusxa). `DEBUG`
o'chiq, brauzerda faqat quruq «500» ko'rinadi — sabab har doim shu yerda.

| Belgi | Sabab |
|---|---|
| `run.sh`: «Baza topilmadi» | `data/db.sqlite3` yo'q — 1-bo'lim, 2-qadam |
| `run.sh`: «Sayt ko'tarilmadi» | ko'rsatilgan loglarda — ko'pincha migratsiya yoki `.env` |
| `502 Bad Gateway` | konteyner ishlamayapti: `docker ps -a`, `docker logs …` |
| `504 Gateway Timeout` | konteyner osilib qolgan: `docker restart inkorporatsion-amayliy-topshiriqlar-uz` |
| Cheksiz `https` ga yo'naltirish | `DJANGO_SSL_REDIRECT=1` qilingan va nginx `X-Forwarded-Proto` ni uzatmayapti |
| Hamma foydalanuvchi chiqib ketdi | `data/.secret_key` o'chgan yoki almashgan |
| `400 Bad Request` | domen `.env` dagi `DJANGO_ALLOWED_HOSTS` da yo'q |
| `attempt to write a readonly database` | `data/` ga yozib bo'lmayapti — `docker restart …` (egasini entrypoint to'g'rilaydi) |
| Rasm/video 404, git'da esa bor | media volume'ga qo'shilmagan — `bash run.sh` |
| `database is locked` | juda kam kutiladi (WAL + 5 s kutish); takrorlansa — PostgreSQL vaqti keldi |

---

## Docker'siz ishga tushirish (zaxira yo'l)

```bash
python -m venv env && env/bin/python -m pip install -r requirements.txt
env/bin/python manage.py migrate
env/bin/python manage.py collectstatic --noinput     # staticfiles/ git'da yo'q — har yangilashda
env/bin/python -m waitress --listen=127.0.0.1:8000 --threads=16 \
    --trusted-proxy=127.0.0.1 "--trusted-proxy-headers=x-forwarded-proto x-forwarded-for" \
    core.wsgi:application
```

Baza, kalit, zaxira va jurnal bu holda loyiha ildizida turadi (`.env` dagi
`DJANGO_DATA_DIR` bilan boshqa joyga ko'chirish mumkin). Shablon, statik va
`.env` o'zgarishi — faqat qayta ishga tushirgandan keyin.

---

## Hozirgi holat qanchaga yetadi

SQLite + WAL shu sayt uchun yetarli: yuk asosan o'qish (sahifalar, videolar),
yozish esa faqat test natijalari va ro'yxatdan o'tish. Bir vaqtda ~50–100
foydalanuvchini bemalol ko'taradi. O'nlab maktab bir vaqtda test
topshiradigan bo'lsa — PostgreSQL'ga o'tish kerak: `core/settings.py` dagi
`DATABASES` va `psycopg` paketi; qolgan kod o'zgarmaydi.
