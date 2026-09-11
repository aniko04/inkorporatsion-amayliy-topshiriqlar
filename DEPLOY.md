# Serverga o'rnatish va yangilash

«Inkorporatsion amaliy topshiriqlar» metodik e-platformasi — Django 5.2 (LTS), SQLite,
statik fayllarni WhiteNoise beradi (alohida nginx sozlash shart emas).

---

## ⚠️ ENG MUHIMI — BAZANI YO'QOTIB QO'YMANG

`db.sqlite3` **git'ga kirmaydi** (2026-09-05 dan, ichida parol hash'lari va
shaxsiy ma'lumot bor). U git tarixidan **oxirgi kommitda** (`426930a`) olib
tashlangan.

Ya'ni: **server hali shu kommitni tortmagan bo'lsa, keyingi `git pull` serverdagi
bazani o'chirib yuboradi** — 1100 ta foydalanuvchi va ularning barcha natijalari
bilan birga. Bu bir martalik xavf, lekin u hali o'tmagan.

Shuning uchun serverda **har doim** quyidagi tartibda yangilang:

```bash
cd /loyiha/yo'li
cp db.sqlite3 ~/db_zaxira_$(date +%F_%H%M).sqlite3   # 1) avval zaxira
git pull                                              # 2) keyin tortish
cp ~/db_zaxira_*.sqlite3 db.sqlite3                   # 3) o'chgan bo'lsa qaytarish
```

Uchinchi qadam faqat baza yo'qolgan bo'lsa kerak — `ls -l db.sqlite3` bilan
tekshiring. Bir marta tortib bo'lgach, keyingi `git pull` lar bazaga tegmaydi.

**Baza git orqali yurmaydi.** Mahalliy kompyuterda admin panel orqali material
qo'shsangiz, u serverga o'z-o'zidan bormaydi — bazani qo'lda ko'chirish kerak
(`scp db.sqlite3 server:/loyiha/yo'li/`). Aksincha ham shunday: serverda
ro'yxatdan o'tgan foydalanuvchilar mahalliy bazada yo'q.

---

## 1. Birinchi o'rnatish

Kerak: **Python 3.11+** (mahalliy muhitda 3.11.3 sinovdan o'tgan).

```bash
git clone <repo> beshbarmoq
cd beshbarmoq

python -m venv env
env/bin/activate                # Windows: env\Scripts\activate

python -m pip install -r requirements.txt   # bitta fayl, waitress ham ichida
```

Bazani mahalliy kompyuterdan ko'chiring (yangi bo'sh baza kerak bo'lsa —
`python manage.py migrate` va `python manage.py createsuperuser`):

```bash
scp db.sqlite3 server:/loyiha/yo'li/
```

`media/` jildi ham (≈350 MB — kitoblar, videolar, muqovalar) ko'chirilishi kerak;
u git'da bor, shuning uchun `git clone` bilan birga keladi.

`.env` (sozlamalar) ham git'da — `git clone` bilan keladi, hech narsa yozish
shart emas. Bazani tayyorlang va statikni yig'ing:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py check --deploy     # xavfsizlik tekshiruvi, pastga qarang
```

---

## 2. `.env` fayli

Barcha sozlamalar — domenlar, HTTPS, HSTS — **bitta `.env` faylida**, loyiha
ildizida. U **git'da turadi**: kompyuterda o'zgartirib push qilasiz, serverda
`git pull` + restart. Nusxa ko'chirish, nomini o'zgartirish yo'q. Har bir
qator nima uchun shunday ekani faylning o'zida izohlangan.

- **Serverda `.env` ni qo'lda tahrirlamang** — keyingi `git pull` «local
  changes would be overwritten» deb to'xtaydi. Tahrir faqat kompyuterda.
- **Yangi domen** — `.env` dagi `DJANGO_ALLOWED_HOSTS` qatoriga. Domenlar
  faqat shu yerda; `core/settings.py` da ro'yxat yo'q. CSRF ro'yxati undan o'zi
  yasaladi.
- Ichida sir yo'q, shuning uchun git'da turishi xavfsiz. Yagona sir —
  maxfiy kalit — pastda.

Hozirgi holat (2026-09-11 dagi server tekshiruviga ko'ra): HTTPS yoqilgan,
`http → https` ni nginx qiladi (Django'da `DJANGO_SSL_REDIRECT=0`, redirect
halqasi xavfi yo'q), HSTS boshida 1 soat va poddomenlarsiz (`www` ga sertifikat
yo'q).

**Sertifikati yo'q domen uchun `DJANGO_HTTPS=1` xavfli** — HSTS yuborilgach,
brauzer u domenni faqat https orqali ochishga urinadi.

### Maxfiy kalit haqida

`SECRET_KEY` endi kodda yozilmagan. Sayt birinchi ishga tushganda loyiha
ildizida `.secret_key` faylini o'zi yaratadi (u `.gitignore` da). Hech narsa
sozlash shart emas.

**Bir marta bo'ladigan ta'sir:** kalit o'zgargani uchun hozir ochiq bo'lgan
barcha sessiyalar bekor bo'ladi — foydalanuvchilar bir marta qaytadan
kirishlari kerak. **Parollarga ta'sir qilmaydi**, hech kim hisobini
yo'qotmaydi.

`.secret_key` faylini **o'chirmang va git'ga qo'shmang**. O'chsa — yangi kalit
yaratiladi va hamma yana bir marta chiqib qoladi.

---

## 3. Saytni ishga tushirish

### Tavsiya etiladigan yo'l — waitress

```bash
python -m waitress --listen=127.0.0.1:8000 --threads=8 \
    --trusted-proxy=127.0.0.1 "--trusted-proxy-headers=x-forwarded-proto x-forwarded-for" \
    core.wsgi:application
```

Waitress toza Python'da yozilgan, Windows'da ham Linux'da ham bir xil ishlaydi
va `requirements.txt` da bor.

**Ikkala `--trusted-proxy` bayrog'i majburiy.** Waitress sukut bo'yicha
nginx yuborgan `X-Forwarded-Proto` va `X-Forwarded-For` ni **o'chirib
tashlaydi** (2026-09-11 da tekshirildi: bayroqsiz Django `127.0.0.1` va `http`
ni ko'radi). Oqibati jim, lekin jiddiy:

- Django HTTPS ekanini bilmaydi — HSTS yuborilmaydi, `DJANGO_SSL_REDIRECT=1`
  bo'lsa esa cheksiz yo'naltirish halqasi;
- har bir foydalanuvchi `127.0.0.1` bo'lib ko'rinadi — kirish cheklovi
  (`home/xavfsizlik.py`) butun sayt uchun **bitta** hisob yuritadi: kimdir
  30 marta parolni xato tersa, 10 daqiqaga **hamma** kira olmay qoladi.

Bayroqlar bilan waitress bu sarlavhalarga faqat `127.0.0.1` dan (ya'ni
nginx'dan) ishonadi, haqiqiy IP ni o'zi aniqlaydi. Qo'shtirnoq bayroqni
o'rab turishi shart: ichidagi bo'sh joy ikki sarlavhani ajratadi.

**`manage.py runserver` ni doimiy ishlatmang.** U ishlab chiqish uchun
mo'ljallangan: bitta oqim (bir vaqtda bitta so'rov — 350 MB lik videolar bor
saytda bu sezilarli sekinlik), avtomatik qayta yuklanish va yuk ostida
sinalmagan xatolarni qayta ishlash bilan. Django o'z hujjatida uni
production'da ishlatmaslikni aniq yozgan.

### Linux — systemd xizmati

`/etc/systemd/system/beshbarmoq.service`:

```ini
[Unit]
Description=Inkorporatsion amaliy topshiriqlar
After=network.target

[Service]
User=www-data
WorkingDirectory=/loyiha/yo'li
ExecStart=/loyiha/yo'li/env/bin/python -m waitress \
          --listen=127.0.0.1:8000 --threads=8 \
          --trusted-proxy=127.0.0.1 "--trusted-proxy-headers=x-forwarded-proto x-forwarded-for" \
          core.wsgi:application
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now beshbarmoq
sudo systemctl status beshbarmoq
```

### Oldindagi nginx

Statikni WhiteNoise beradi, shuning uchun nginx faqat proksi bo'lib turadi.
**`X-Forwarded-Proto` ni uzatish majburiy** — Django HTTPS ekanini shundan biladi:

```nginx
server {
    listen 443 ssl;
    server_name aniko.uz www.aniko.uz;

    # ssl_certificate ... (certbot yozadi)

    client_max_body_size 100M;      # admin paneldan katta PDF yuklash uchun

    location / {
        proxy_pass         http://127.0.0.1:8000;
        proxy_set_header   Host              $host;
        proxy_set_header   X-Real-IP         $remote_addr;
        proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;   # ← shusiz Django HTTPS ni bilmaydi
    }
}
```

---

## 4. Yangilash (kod o'zgargandan keyin)

```bash
cd /loyiha/yo'li
cp db.sqlite3 ~/db_zaxira_$(date +%F_%H%M).sqlite3

git pull
env/bin/python -m pip install -r requirements.txt   # paketlar o'zgargan bo'lsa
env/bin/python manage.py migrate
env/bin/python manage.py collectstatic --noinput
sudo systemctl restart beshbarmoq
```

**Qayta ishga tushirish majburiy**, hatto faqat shablon o'zgargan bo'lsa ham:

- `DEBUG=False` bo'lgani uchun Django shablonlarni keshlaydi — `.html` o'zgarishi
  qayta ishga tushirmaguncha ko'rinmaydi;
- WhiteNoise `staticfiles/` ni **faqat bir marta, ishga tushishda** o'qiydi —
  yangi qo'shilgan fayl qayta ishga tushirmaguncha 404 qaytaradi (sahifa
  uslubsiz, rasmlarsiz ochiladi);
- `.env` ham faqat ishga tushishda o'qiladi.

`git pull` «untracked working tree file '.env' would be overwritten» deb
to'xtasa — serverda eski, qo'lda yozilgan `.env` qolgan: uni o'chirib
(`rm .env`), pull'ni qaytaring. Bir martalik holat.

---

## 5. Zaxira nusxa

**Buning uchun hech narsa qilish shart emas — o'zi ishlaydi.** Sayt har ishga
tushganda bazani tekshiradi va oxirgi nusxa 24 soatdan eski bo'lsa yangisini
oladi. Nusxalar `zaxira/` jildida, oxirgi **14 tasi** saqlanadi (eskisi o'zi
o'chib boradi). Jild git'ga kirmaydi.

Qo'lda olish kerak bo'lsa — masalan, katta o'zgarishdan oldin:

```bash
python manage.py zaxira            # yangi nusxa
python manage.py zaxira --royxat   # bor nusxalarni ko'rish
python manage.py zaxira --jild D:/zaxiralar    # boshqa joyga
```

Nusxa SQLite'ning o'z `.backup` amali bilan olinadi — sayt ishlab turganda ham
butun va izchil chiqadi. **Oddiy `cp` bilan nusxalamang**: baza WAL rejimida
ishlaydi, oxirgi yozuvlar `db.sqlite3-wal` faylida bo'lishi mumkin va ular
nusxaga tushmay qoladi.

Nusxadan tiklash — shunchaki fayl nomini almashtirish:

```bash
# saytni to'xtating, keyin:
cp zaxira/db_2026-09-09_140905.sqlite3 db.sqlite3
```

### Media fayllarni ham unutmang

`zaxira` faqat bazani oladi. `media/` jildi (≈350 MB — kitoblar, videolar)
git'da bor, lekin admin panel orqali yangi fayl yuklansangiz uni ham
saqlab qo'ying:

```bash
tar czf /zaxira/media_$(date +%F).tar.gz media/     # Linux
Compress-Archive media D:\zaxiralar\media.zip       # Windows PowerShell
```

**Eng muhim maslahat:** `zaxira/` jildini vaqti-vaqti bilan boshqa diskka yoki
bulutga ko'chirib turing. U loyiha ichida turibdi — jild butunlay o'chib ketsa,
nusxalar ham u bilan ketadi.

---

## 5b. Saytni SHAXSIY KOMPYUTERDAN turg'izish (vaqtinchalik)

Server tayyor bo'lgunicha saytni o'z kompyuteringizdan ishlatish mumkin, lekin
bunda **kompyuteringiz internetga ochiladi** — quyidagilarga rioya qiling.

### Qaysi yo'l bilan ochish

| Yo'l | Xavfsizlik | Izoh |
|---|---|---|
| **Cloudflare Tunnel** (tavsiya) | ✅ eng xavfsiz | Kompyuterda **birorta port ochilmaydi**. Tunnel o'zi Cloudflare'ga ulanadi, HTTPS ham tekin. Uy routeri sozlanmaydi. |
| Router'da port ochish (port forwarding) | ⚠️ xavfli | Kompyuteringiz to'g'ridan-to'g'ri butun internetga ochiladi. Skanerlovchi robotlar bir necha daqiqada topadi. |
| Faqat mahalliy tarmoq | ✅ | `runserver` standart holda faqat shu kompyuterda ochiladi. |

Cloudflare Tunnel bilan:

```bash
# 1-terminal: sayt (faqat kompyuterning o'zida tinglaydi; bayroqlar — 3-bo'limga qarang)
env\Scripts\python.exe -m waitress --listen=127.0.0.1:8000 --threads=8 --trusted-proxy=127.0.0.1 "--trusted-proxy-headers=x-forwarded-proto x-forwarded-for" core.wsgi:application

# 2-terminal: tunnel
cloudflared tunnel --url http://127.0.0.1:8000
```

### Majburiy qoidalar

1. **`0.0.0.0` ga bog'lamang** — `runserver 0.0.0.0:8000` kompyuterni butun
   tarmoqqa ochadi. `127.0.0.1` da qoldiring, tashqariga tunnel chiqarsin.
2. **`DJANGO_DEBUG=1` qilmang.** Hozir `DEBUG=False` va tekshirilgan: xato
   sahifasi kod, yo'l yoki sozlama oshkor qilmaydi. `1` qilsangiz — qiladi.
3. **Kompyuterni uxlatib qo'ymang** (Windows: Settings → Power → Sleep: Never),
   aks holda sayt tunda o'chadi.
4. **Antivirus va Windows Defender yoqiq tursin.** Bu vaqtincha yechim —
   kompyuterda shaxsiy fayllaringiz ham bor.
5. **Boshqa xizmatlarni ochmang** — ayniqsa masofaviy ish stoli (RDP, 3389-port)
   va fayl almashish (SMB, 445-port). Bular eng ko'p hujum qilinadigan portlar.
6. **2–3 kundan keyin to'xtating.** Bu doimiy yechim emas.

### Saytda nima himoya qilingan

Quyidagilar tekshirilgan va ishlaydi:

- **Maxfiy fayllar tashqaridan olinmaydi.** `db.sqlite3`, `.env`, `.secret_key`,
  `logs/`, `zaxira/`, `malumotlar/`, `.git/`, `core/settings.py` — hammasi 404.
  Yo'l orqali chiqib ketish (`/media/../db.sqlite3`) ham bloklangan.
- **Parol terish cheklangan** (`home/xavfsizlik.py`): `/admin/` ga 10 ta xato
  urinishdan keyin IP 15 daqiqaga bloklanadi, oddiy kirishga 30 tadan keyin
  10 daqiqaga. Robot minglab urinish qiladi — birinchi soniyalardayoq to'xtaydi.
  Haqiqiy foydalanuvchi buni sezmaydi (chegara ataylab yuqori: bir maktabning
  hamma o'quvchisi bitta IP ostida bo'lishi mumkin).
- **Bloklangan urinishlar `logs/xato.log` ga yoziladi** — kimdir urinayotganini
  shu yerdan ko'rasiz: `findstr "Kirish cheklovi" logs\xato.log`

### Kundalik nazorat

```bash
type logs\xato.log | findstr /C:"Kirish cheklovi"    # hujum urinishlari
python manage.py zaxira --royxat                     # zaxiralar joyidami
```

---

## 6. Xavfsizlik tekshiruvi

```bash
python manage.py check --deploy
```

Uchta ogohlantirish chiqadi — uchalasi ham `.env` da **ataylab**:

- `security.W005` — HSTS poddomenlarga tarqatilmagan (`www` ga sertifikat yo'q);
- `security.W008` — Django o'zi https'ga yo'naltirmaydi (buni nginx qiladi);
- `security.W021` — `SECURE_HSTS_PRELOAD` yoqilmagan.

Preload — domenni brauzerlarning ichki ro'yxatiga qo'shish; undan chiqish oylar
oladi va shu vaqt davomida sayt HTTPS'siz umuman ochilmaydi. Sayt uzoq vaqt
barqaror ishlagach, `.env` da `DJANGO_HSTS_PRELOAD=1` bilan yoqish mumkin.

Boshqa ogohlantirish chiqsa (masalan `W004`, `W012`, `W016`) — `.env` o'qilmayapti.

Nima yoqilgan: HTTPS'ga yo'naltirish (nginx), HSTS (hozircha 1 soat),
`Secure` + `HttpOnly` + `SameSite=Lax` cookie'lar, `X-Frame-Options: DENY`
(media uchun `SAMEORIGIN` — PDF ko'ruvchisi ishlashi uchun),
`X-Content-Type-Options: nosniff`, `Referrer-Policy: same-origin`.

---

## 7. Xatolarni topish

Xatolar `logs/xato.log` ga yoziladi (2 MB dan oshsa aylanadi, 5 ta eski nusxa
saqlanadi). `DEBUG=False` bo'lgani uchun brauzerda faqat quruq «500» ko'rinadi —
sabab har doim shu faylda.

```bash
tail -50 logs/xato.log
```

| Belgi | Sabab |
|---|---|
| `504 Gateway Timeout` (1 daqiqa kutib) | nginx ishlayapti, Django/waitress javob bermayapti — `sudo systemctl status beshbarmoq` |
| `502 Bad Gateway` (darhol) | Django/waitress umuman ishga tushmagan — xato `logs/xato.log` yoki `journalctl -u beshbarmoq` da |
| Sayt cheksiz `https` ga yo'naltiraveradi | `.env` da `DJANGO_SSL_REDIRECT=1` qilingan va nginx `X-Forwarded-Proto` ni uzatmayapti |
| Barcha foydalanuvchilar chiqib ketdi | `.secret_key` o'chgan yoki o'zgargan (yuqoriga qarang) |
| Sahifa uslubsiz, rasmlar yo'q | `collectstatic` qilinmagan **yoki** qayta ishga tushirilmagan |
| `.html` o'zgarishi ko'rinmayapti | shablon keshi — qayta ishga tushiring |
| Rasm yarmigacha yuklanadi | WhiteNoise eski indeks bilan ishlayapti — qayta ishga tushiring |
| `400 Bad Request` / `DisallowedHost` | domen `.env` dagi `DJANGO_ALLOWED_HOSTS` da yo'q |
| `database is locked` | juda kam kutiladi (WAL + 5s kutish yoqilgan); takrorlansa PostgreSQL'ga o'tish vaqti keldi |

---

## 8. Hozirgi holat qanchaga yetadi

SQLite + WAL rejimi shu sayt uchun yetarli: yuk asosan **o'qish** (sahifalar,
videolar), yozish esa faqat test natijalari va ro'yxatdan o'tish — kuniga bir
necha yuz marta. Bir vaqtning o'zida ~50–100 foydalanuvchini bemalol ko'taradi.

O'nlab maktab bir vaqtda test topshiradigan bo'lsa — PostgreSQL'ga o'tish
kerak bo'ladi. Unda `core/settings.py` dagi `DATABASES` blokini almashtirish
va `psycopg` qo'shish yetarli; qolgan kod o'zgarmaydi.
