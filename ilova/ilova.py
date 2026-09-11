# -*- coding: utf-8 -*-
"""
«Inkorporatsion amaliy topshiriqlar» — Windows uchun ish stoli ilovasi.

Sayt Windows ning O'Z brauzer dvigateli — Edge WebView2 (Chromium) — ichida
ochiladi. Ya'ni saytdagi hamma narsa brauzerdagidek ishlaydi: JavaScript
(krossvordlar, testlar, taymer), H.264 videolar, PDF ko'ruvchi, cookie va
sessiya (bir marta kirilsa, keyingi safar ham kirilgan holda qoladi).

Ilova PYTHON O'RNATILMAGAN kompyuterda ham ishlaydi — PyInstaller hamma
narsani bitta .exe ichiga joylaydi. Yagona tashqi shart: Edge WebView2
Runtime, u Windows 10/11 da Edge bilan birga allaqachon o'rnatilgan
bo'ladi; bo'lmasa ilova buni tushuntiruvchi oyna ko'rsatadi.
"""

import os
import sys
import threading
import urllib.request
import urllib.error


# ============================================================
#  SOZLAMALAR
# ============================================================

ILOVA_NOMI = "Inkorporatsion amaliy topshiriqlar"

# Ilova shu manzillarni NAVBATMA-NAVBAT tekshiradi va ishlayotgan
# BIRINCHISINI ochadi. Domen hali ulanmagan bo'lsa ham ilova ishlayveradi.
#
# Bu ro'yxatni QAYTA QURMASDAN o'zgartirish mumkin: .exe yonida
# `manzil.txt` fayli yaratilsa, ilova o'sha fayldagi manzillarni oladi
# (har qatorda bitta manzil, `#` bilan boshlangan qator — izoh).
MANZILLAR = [
    "https://inkorporatsion-amaliy-topshiriqlar.uz",
    "https://texnoedu.uz",
]

# Manzilni tekshirish uchun kutish vaqti (soniya). Qisqa bo'lgani ma'qul:
# ulanmagan domen shuncha vaqtdan keyin tashlab ketiladi.
KUTISH = 6

OYNA_ENI = 1360
OYNA_BOYI = 860
ENG_KICHIK_ENI = 900
ENG_KICHIK_BOYI = 600


# ============================================================
#  YORDAMCHI FUNKSIYALAR
# ============================================================

def ilova_papkasi():
    """.exe (yoki .py) turgan papka — `manzil.txt` shu yerdan izlanadi."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def manzillarni_oq():
    """`manzil.txt` bo'lsa — o'shani, bo'lmasa — ichki ro'yxatni qaytaradi."""
    fayl = os.path.join(ilova_papkasi(), 'manzil.txt')
    try:
        with open(fayl, encoding='utf-8-sig') as f:
            royxat = []
            for qator in f:
                qator = qator.strip()
                if not qator or qator.startswith('#'):
                    continue
                if not qator.startswith(('http://', 'https://')):
                    qator = 'https://' + qator
                royxat.append(qator)
        if royxat:
            return royxat
    except OSError:
        pass
    return list(MANZILLAR)


def ishlayaptimi(manzil):
    """Manzil javob berayaptimi? 4xx ham «sayt bor» degani (masalan 404)."""
    sorov = urllib.request.Request(
        manzil,
        method='GET',
        # Ba'zi serverlar User-Agent siz so'rovni rad etadi.
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'},
    )
    try:
        with urllib.request.urlopen(sorov, timeout=KUTISH):
            return True
    except urllib.error.HTTPError:
        # Server javob berdi — demak sayt bor, faqat shu sahifa yo'q.
        return True
    except Exception:
        return False


def ishlaydigan_manzil():
    """Ro'yxatdagi birinchi ishlaydigan manzil; hech biri bo'lmasa None."""
    for manzil in manzillarni_oq():
        if ishlayaptimi(manzil):
            return manzil
    return None


# ============================================================
#  ULANISH YO'Q BO'LGANDAGI SAHIFA
# ============================================================

def oflayn_sahifa(manzillar):
    """Internet yo'qligini o'zbekcha tushuntiruvchi, sayt uslubidagi sahifa."""
    royxat = ''.join('<li>%s</li>' % m for m in manzillar)
    return """<!DOCTYPE html>
<html lang="uz"><head><meta charset="utf-8">
<title>Ulanib bo'lmadi</title>
<style>
  * { box-sizing: border-box; }
  body {
    margin: 0; min-height: 100vh;
    display: flex; align-items: center; justify-content: center;
    background: linear-gradient(180deg, #DCEEFB 0%%, #F2F7FC 100%%);
    font-family: 'Segoe UI', system-ui, sans-serif; color: #23405F;
  }
  .quti {
    max-width: 620px; margin: 24px; padding: 40px 44px;
    background: #fff; border-radius: 28px; text-align: center;
    box-shadow: 0 18px 44px rgba(30, 60, 110, .16);
  }
  .belgi {
    width: 84px; height: 84px; margin: 0 auto 20px;
    display: flex; align-items: center; justify-content: center;
    border-radius: 50%%; background: #FDECEC; font-size: 40px;
  }
  h1 { margin: 0 0 12px; font-size: 1.7rem; color: #1F3A5F; }
  p  { margin: 0 0 10px; font-size: 1.02rem; line-height: 1.6; color: #46617F; }
  ul { margin: 14px auto 22px; padding: 14px 18px; max-width: 460px;
       list-style: none; text-align: left;
       background: #F4F8FC; border-radius: 16px;
       font-size: .93rem; color: #35506F; word-break: break-all; }
  li { padding: 3px 0; }
  button {
    padding: 13px 34px; border: 0; border-radius: 999px;
    background: linear-gradient(180deg, #4E9AF2, #2E7DE0);
    color: #fff; font: 600 1.05rem 'Segoe UI', sans-serif; cursor: pointer;
    box-shadow: 0 4px 0 #1E62C4, 0 10px 20px rgba(20, 50, 100, .22);
  }
  button:active { transform: translateY(2px); box-shadow: 0 2px 0 #1E62C4; }
  .izoh { margin-top: 20px; font-size: .87rem; color: #7A8CA3; }
</style></head>
<body>
  <div class="quti">
    <div class="belgi">&#128246;</div>
    <h1>Saytga ulanib bo'lmadi</h1>
    <p>Internet aloqasi yo'q yoki sayt vaqtincha ishlamayapti.</p>
    <p>Quyidagi manzillar tekshirildi:</p>
    <ul>%s</ul>
    <button onclick="location.reload()">Qayta urinish</button>
    <p class="izoh">
      Aloqani tekshiring va «Qayta urinish» tugmasini bosing.
      Sayt manzili o'zgargan bo'lsa, ilova yonidagi
      <b>manzil.txt</b> faylida to'g'rilash mumkin.
    </p>
  </div>
</body></html>""" % royxat


def webview_yoq_xabari(xato):
    """WebView2 Runtime topilmaganda — nima qilish kerakligini aytadi."""
    import ctypes
    matn = (
        "Ilovani ochib bo'lmadi.\n\n"
        "Sabab: Windows'ning «Edge WebView2 Runtime» komponenti topilmadi.\n"
        "Sayt shu komponent yordamida ko'rsatiladi.\n\n"
        "Yechim: quyidagi manzildan bepul yuklab o'rnating:\n"
        "https://go.microsoft.com/fwlink/p/?LinkId=2124703\n\n"
        "(Texnik ma'lumot: %s)" % xato
    )
    ctypes.windll.user32.MessageBoxW(0, matn, ILOVA_NOMI, 0x10)


# ============================================================
#  ISHGA TUSHIRISH
# ============================================================

def main():
    import webview

    manzillar = manzillarni_oq()

    # Manzilni tekshirish sekin bo'lishi mumkin, shuning uchun oyna DARHOL
    # ochiladi (kutish ekrani bilan), tekshiruv esa fonda ketadi.
    oyna = webview.create_window(
        ILOVA_NOMI,
        html=KUTISH_SAHIFASI,
        width=OYNA_ENI,
        height=OYNA_BOYI,
        min_size=(ENG_KICHIK_ENI, ENG_KICHIK_BOYI),
        background_color='#DCEEFB',
        text_select=True,
    )

    def yukla():
        manzil = ishlaydigan_manzil()
        if manzil:
            oyna.load_url(manzil)
        else:
            oyna.load_html(oflayn_sahifa(manzillar))

    def boshlanganda():
        threading.Thread(target=yukla, daemon=True).start()

    # Sessiya (kirgan foydalanuvchi, cookie) shu papkada saqlanadi, shuning
    # uchun ilova qayta ochilganda qaytadan login qilish shart emas.
    saqlash = os.path.join(
        os.environ.get('LOCALAPPDATA', os.path.expanduser('~')),
        'InkorporatsionTopshiriqlar',
    )
    try:
        os.makedirs(saqlash, exist_ok=True)
    except OSError:
        saqlash = None

    try:
        webview.start(
            boshlanganda,
            gui='edgechromium',      # Chromium dvigateli — eski IE emas
            private_mode=False,      # cookie/sessiya saqlansin
            storage_path=saqlash,
            debug=False,
        )
    except Exception as xato:      # WebView2 yo'q yoki ishga tushmadi
        webview_yoq_xabari(xato)
        sys.exit(1)


# Oyna ochilishi bilan ko'rinadigan kutish ekrani (manzil tekshirilguncha).
KUTISH_SAHIFASI = """<!DOCTYPE html>
<html lang="uz"><head><meta charset="utf-8"><title>Yuklanmoqda…</title>
<style>
  body { margin: 0; height: 100vh; display: flex; align-items: center;
         justify-content: center; flex-direction: column; gap: 22px;
         background: linear-gradient(180deg, #DCEEFB 0%, #F2F7FC 100%);
         font-family: 'Segoe UI', system-ui, sans-serif; color: #2E7DE0; }
  .halqa { width: 54px; height: 54px; border-radius: 50%;
           border: 5px solid #C7DFF6; border-top-color: #2E7DE0;
           animation: aylan .9s linear infinite; }
  @keyframes aylan { to { transform: rotate(360deg); } }
  p { margin: 0; font-size: 1.05rem; font-weight: 600; }
  small { color: #7A8CA3; font-weight: 400; }
</style></head>
<body>
  <div class="halqa"></div>
  <p>Inkorporatsion amaliy topshiriqlar</p>
  <small>Saytga ulanmoqda…</small>
</body></html>"""


if __name__ == '__main__':
    main()
