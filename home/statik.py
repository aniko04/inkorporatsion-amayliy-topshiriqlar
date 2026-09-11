"""Statik va media fayllarni WhiteNoise orqali berish.

Statik (`/static/`) — oddiy WhiteNoise: `staticfiles/` ishga tushishda bir
marta ro'yxatga olinadi va oldindan siqilgan (gzip) holda beriladi.

Media (`/media/`) — shu moduldagi qo'shimcha. Ilgari uni Django'ning
`django.views.static.serve` view'i berardi, u esa uch narsani bilmaydi:
  • `Range` so'rovi — videoni o'rtasiga o'tkazib bo'lmaydi, Safari/iOS esa
    videoni umuman ijro etmaydi (u 206 javobini talab qiladi);
  • `Cache-Control` — brauzer faylni yoshiga qarab o'zicha keshlaydi
    (`home/models.py` dagi `_versiyali` izohiga qarang);
  • samaradorlik — Django hujjati uni production uchun emas deb yozadi.
WhiteNoise bularning hammasini qiladi: 206, ETag/304, Cache-Control.

NEGA MEDIA RO'YXATGA OLINMAYDI: WhiteNoise statikni ishga tushishda bir marta
indekslaydi va har faylning o'lchamini eslab qoladi. Media esa ish vaqtida
o'zgaradi — admin paneldan yangi fayl yuklanadi. Indeksda bo'lsa, yangi fayl
qayta ishga tushirilguncha 404 qaytarardi, o'sha nom bilan almashtirilgani
esa eski `Content-Length` bilan chala berilardi. Shuning uchun media har
so'rovda diskdan qidiriladi — bitta `stat()`, sezilmaydigan narx.
"""

import os
from urllib.parse import urlparse

from django.conf import settings
from whitenoise.middleware import WhiteNoiseMiddleware
from whitenoise.responders import NotARegularFileError
from whitenoise.string_utils import ensure_leading_trailing_slash


class StatikVaMedia(WhiteNoiseMiddleware):
    """`whitenoise.middleware.WhiteNoiseMiddleware` + `/media/`."""

    def __init__(self, get_response=None, settings=settings):
        super().__init__(get_response, settings)
        self.media_prefix = ensure_leading_trailing_slash(urlparse(settings.MEDIA_URL).path)
        # realpath: jild symlink bo'lsa ham chegara tekshiruvi to'g'ri ishlasin.
        self.media_root = os.path.realpath(settings.MEDIA_ROOT) + os.sep

    def __call__(self, request):
        if request.path_info.startswith(self.media_prefix):
            fayl = self._media_fayli(request.path_info)
            if fayl is not None:
                javob = self.serve(fayl, request)
                # PDF ko'ruvchi (<iframe>) o'z saytimizda ochilsin, begona saytda
                # esa yo'q. XFrameOptionsMiddleware bu javobni ko'rmaydi: WhiteNoise
                # undan oldin turadi va javobni o'zi qaytaradi.
                javob['X-Frame-Options'] = 'SAMEORIGIN'
                javob['Accept-Ranges'] = 'bytes'
                return javob
        return super().__call__(request)

    def _media_fayli(self, url):
        """URL ga mos media fayl; topilmasa None (so'rov oddiy 404 ga o'tadi)."""
        # `..`, `//`, `\` bo'lgan manzil — jilddan tashqariga chiqish urinishi.
        if url.endswith('/') or not self.url_is_canonical(url):
            return None
        try:
            yol = os.path.realpath(os.path.join(self.media_root, url[len(self.media_prefix):]))
            if not self.path_is_child_of(yol, self.media_root):
                return None
            return self.get_static_file(yol, url)
        except (NotARegularFileError, ValueError):
            # Yo'q, jild yoki oddiy fayl emas; ValueError — manzilda NUL belgisi.
            return None
