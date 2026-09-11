# Inkorporatsion amaliy topshiriqlar

Boshlang'ich sinf texnologiya fanini inkorporatsion yondashuv asosida o'qitish
bo'yicha metodik e-platforma: o'qituvchilar uchun yetti bo'lim va bolalar uchun
10 ta interaktiv mashq. Django 5.2 (LTS), SQLite, WhiteNoise.

## Serverda (Docker)

```bash
git pull && bash run.sh
```

Birinchi o'rnatish, baza, nginx, zaxira va xatolar — [DEPLOY.md](DEPLOY.md).

## Mahalliy kompyuterda

```bash
python -m venv env
env/Scripts/python.exe -m pip install -r requirements.txt
env/Scripts/python.exe manage.py migrate
env/Scripts/python.exe manage.py collectstatic --noinput
env/Scripts/python.exe manage.py runserver
```

`DEBUG` ishlab chiqishda ham o'chiq, shuning uchun `collectstatic` shart va
shablon o'zgarishi server qayta ishga tushirilgandagina ko'rinadi. Loyiha
bo'yicha batafsil eslatmalar — [CLAUDE.md](CLAUDE.md).
